from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .utils import *
from ..serializers import *

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
        
        serializer = NoticiaListSerializer(noticias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error al obtener noticias públicas: {e}", exc_info=True)
        return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

