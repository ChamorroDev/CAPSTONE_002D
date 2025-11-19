from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .utils import *
from ..serializers import *
import logging
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class NoticiaListCreateView(generics.ListCreateAPIView):
    serializer_class = NoticiaSerializer
    permission_classes = [IsAuthenticated, PuedeGestionarNoticias]
    
    def get_queryset(self):
        return Noticia.objects.filter(junta_vecinos=self.request.user.junta_vecinos)
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user, junta_vecinos=self.request.user.junta_vecinos)

class NoticiaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoticiaSerializer
    permission_classes = [IsAuthenticated, PuedeGestionarNoticias]
    
    def get_queryset(self):
        return Noticia.objects.filter(junta_vecinos=self.request.user.junta_vecinos)



@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def detalle_noticia_api(request, noticia_id):
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        serializer = NoticiaDetalleSerializer(noticia)
        return Response(serializer.data)
        
    except Noticia.DoesNotExist:
        return Response({'error': 'Noticia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([EsDirectivo])
def noticia_list_create(request):
    user = request.user
    junta_vecinos = user.junta_vecinos
    
    noticias = Noticia.objects.filter(junta_vecinos=junta_vecinos).order_by('-fecha_creacion')

    if request.method == 'GET':
        serializer = NoticiaListSerializer(noticias, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = NoticiaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(autor=user, junta_vecinos=junta_vecinos)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([EsDirectivo])
def noticia_detail_update_delete(request, pk):
    user = request.user
    
    try:
        noticia = Noticia.objects.get(pk=pk, junta_vecinos=user.junta_vecinos)
    except Noticia.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = NoticiaDetalleSerializer(noticia)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = NoticiaSerializer(noticia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        noticia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([EsDirectivo])
def subir_imagen_noticia(request):

    noticia_id = request.data.get('noticia')
    imagenes = request.FILES.getlist('imagen')

    if not noticia_id:
        return Response({'error': 'ID de noticia es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
    except Noticia.DoesNotExist:
        return Response({'error': 'Noticia no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if not imagenes:
        return Response({'error': 'No se han enviado imágenes.'}, status=status.HTTP_400_BAD_REQUEST)

    created_images = []
    for imagen in imagenes:
        data = {'noticia': noticia.id, 'imagen': imagen}
        serializer = NoticiaImagenSerializer(data=data)
        if serializer.is_valid():
            created_images.append(serializer.save())
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    response_serializer = NoticiaImagenSerializer(created_images, many=True)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([EsDirectivo])
def eliminar_imagen_noticia(request, pk):

    try:
        imagen = NoticiaImagen.objects.get(id=pk)
    except NoticiaImagen.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    imagen.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@permission_classes([EsDirectivo])
def set_imagen_principal(request, pk):

    try:
        noticia = Noticia.objects.get(pk=pk, junta_vecinos=request.user.junta_vecinos)
    except Noticia.DoesNotExist:
        return Response({'error': 'Noticia no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    imagen_principal_id = request.data.get('imagen_principal')
    
    if not imagen_principal_id:
        return Response({'error': 'ID de imagen principal es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        imagen = NoticiaImagen.objects.get(id=imagen_principal_id, noticia=noticia)
    except NoticiaImagen.DoesNotExist:
        return Response({'error': 'La imagen no pertenece a esta noticia'}, status=status.HTTP_400_BAD_REQUEST)

    noticia.imagen_principal_id = imagen_principal_id
    noticia.save()

    return Response({
        'success': True,
        'message': 'Imagen principal actualizada correctamente',
        'imagen_principal_id': imagen_principal_id
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def noticias_publicas_api(request):

    try:
        noticias = Noticia.objects.filter(es_publica=True).order_by('-fecha_creacion')
        print("-> Obteniendo noticias públicas...") 
        print(f"   -> Total noticias encontradas: {noticias}")
        for noticia in noticias:
            print(f"      - Noticia: | Fecha: {noticia.autor}")
        serializer = NoticiaListSerializer(noticias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error al obtener noticias públicas: {e}", exc_info=True)
        return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def save_image_from_url(model_instance, url, field_name='imagen_principal'):
    """
    Descarga una imagen desde una URL y la guarda en el ImageField especificado 
    de la instancia del modelo.
    
    Args:
        model_instance (Noticia): La instancia de Noticia que se está actualizando.
        url (str): La URL de la imagen a descargar.
        field_name (str): El nombre del ImageField en el modelo (default: 'imagen_principal').
    """
    if not url:
        print("   -> No se proporcionó URL de imagen.")
        return
        
    try:
        print(f"   -> Noticia intentando guardar imagen: {model_instance.titulo}")

        # 1. Realizar la petición HTTP para descargar la imagen
        response = requests.get(url, stream=True, timeout=40)
        response.raise_for_status() # Lanza un error para códigos de estado 4xx/5xx

        # 2. Determinar el nombre del archivo
        filename = os.path.basename(url).split('?')[0]
        if not filename or '.' not in filename:
             # Nombre de archivo de respaldo si no se puede determinar
             ext = response.headers.get('Content-Type', '').split('/')[-1]
             if ext not in ['jpeg', 'png', 'jpg']:
                ext = 'jpg'
             filename = f"noticia_web_{model_instance.pk}_{int(time.time())}.{ext}"

        # 3. Guardar la imagen en el ImageField
        image_field = getattr(model_instance, field_name)
        
        # Usamos ContentFile para envolver el contenido binario y guardarlo
        image_field.save(
            filename, 
            ContentFile(response.content), 
            save=True
        )
        print(f"   -> Imagen guardada con éxito para {model_instance.titulo}.")

    except requests.exceptions.RequestException as e:
        print(f"   -> Advertencia: Error al descargar la imagen de {url}: {e}")
    except Exception as e:
        print(f"   -> Error inesperado al guardar la imagen: {e}")



class IsInternalAPICall(permissions.BasePermission):
    """
    Permite el acceso solo si la clave X-API-KEY en los headers coincide 
    con la definida en DJANGO_INTERNAL_API_KEY en settings.
    
    Utiliza secrets.compare_digest para una comparación segura contra ataques de tiempo.
    """
    message = "Acceso denegado: API Key interna inválida o faltante."

    def has_permission(self, request, view):
        # 1. Obtener la clave enviada en el header
        api_key_sent = request.headers.get('X-API-KEY')

        # 2. Obtener la clave esperada de settings
        expected_key = getattr(settings, 'WEBHOOK_TOKEN', None)

        # 3. Validación de existencia
        if not expected_key:
            logger.error("DJANGO_INTERNAL_API_KEY no definida en settings. Acceso denegado.")
            return False 

        if not api_key_sent:
            logger.warning("Intento de acceso a la API de carga sin X-API-KEY.")
            return False

        # 4. Comparación segura
        return secrets.compare_digest(api_key_sent, expected_key)


class NoticiaCargarAPIView(APIView):
    """
    Endpoint para recibir una lista de noticias de la web de Vitacura.
    Maneja la deduplicación y la descarga de imágenes.
    """
    # Si usas API Keys personalizadas, este es el lugar para definir tu permiso.
    permission_classes = [IsInternalAPICall] 

    def post(self, request, *args, **kwargs):
        # El scraper envía una lista de objetos, no un solo objeto
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"detail": "Se espera una lista de noticias para procesar."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Usamos el serializador con many=True para procesar la lista
        serializer = NoticiaScraperSerializer(data=data, many=True)
        # Procesamiento y guardado de noticias
        noticias_creadas_count = 0
        noticias_omitidas_count = 0
        
        for noticia_data in data:
            titulo = noticia_data['titulo']
            url_origen = noticia_data['link_imagen']
            
            # --- 1. Lógica de Deduplicación ---
            # Buscamos por título. Si ya existe, la omitimos.
            if Noticia.objects.filter(titulo=titulo).exists():
                logger.info(f"Noticia omitida (Duplicado por título): {titulo}")
                noticias_omitidas_count += 1
                continue

            # --- 2. Preparación de datos para ForeignKeys ---
            # Usamos get_object_or_404 o get() aquí, pero para un script automático
            # es mejor usar un try/except o confiar en los IDs si son constantes.
            try:
                autor = CustomUser.objects.get(pk=66)
                junta_vecinos = JuntaVecinos.objects.get(pk=(15))
            except (CustomUser.DoesNotExist, JuntaVecinos.DoesNotExist) as e:
                logger.error(f"Error de Foreign Key: {e} - Omitiendo noticia: {titulo}")
                noticias_omitidas_count += 1
                continue

            # --- 3. Guardado en la Base de Datos (Transacción segura) ---
            try:
                with transaction.atomic():
                    # Extraer la URL de la imagen antes de crear la instancia
                    link_imagen = noticia_data.pop('link_imagen', '')
                    
                    # Crear la instancia de Noticia con los campos restantes
                    noticia = Noticia.objects.create(
                        titulo=titulo,
                        contenido=noticia_data['contenido_completo'],
                        fecha_creacion=noticia_data['fecha_noticia'],
                        es_publica=1,
                        autor=autor,
                        junta_vecinos=junta_vecinos,
                    )
                    print(f"   -> Noticia creada: {titulo}")
                    # --- 4. Descarga y guardado de la Imagen ---
                    # Esto debe ejecutarse DESPUÉS de guardar la Noticia para tener el PK
                    save_image_from_url(noticia, link_imagen)

                    noticias_creadas_count += 1
                    logger.info(f"Noticia creada con éxito: {titulo}")

            except IntegrityError as e:
                logger.error(f"Error de integridad al crear la noticia {titulo}: {e}")
                noticias_omitidas_count += 1
            except Exception as e:
                logger.error(f"Error desconocido al procesar la noticia {titulo}: {e}")
                noticias_omitidas_count += 1

        # --- 5. Respuesta Final ---
        return Response(
            {
                "detail": "Procesamiento de noticias finalizado.",
                "creadas": noticias_creadas_count,
                "omitidas_duplicadas": noticias_omitidas_count
            },
            status=status.HTTP_200_OK
        )