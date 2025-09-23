import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from PIL import Image
from django.db.models import Case, When, Value, ExpressionWrapper, FloatField, F
from django.db.models.functions import ExtractYear, ExtractMonth
import io
import json
from django.conf import settings 
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .certificado import generar_certificado_pdf_vecino
from django.db.models import Q
import base64
import traceback
# views.py
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import IntegrityError
from django.utils import timezone
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import now
from django.db.models.functions import ExtractMonth
from django.contrib.auth.hashers import make_password
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .models import *
from .serializers import *
import re
from django.db.models import Count
from datetime import datetime, time
# ----- RESPUESTAS JSON -----

class JSONResponseOkRows(HttpResponse):
    def __init__(self, data, msg, **kwargs):
        data = {"OK": True, "count": len(data), "registro": data, "msg": msg}
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super().__init__(content, **kwargs)

class JSONResponseOk(HttpResponse):
    def __init__(self, data, msg, **kwargs):
        data = {"OK": True, "count": 1, "registro": data, "msg": msg}
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super().__init__(content, **kwargs)

class JSONResponseErr(HttpResponse):
    def __init__(self, data, **kwargs):
        data = {"OK": False, "count": 0, "msg": data}
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super().__init__(content, **kwargs)
# ===================== BASES GENÉRICAS PARA EVITAR REPETIR =====================


def generar_certificado_pdf(request):

    buffer = io.BytesIO()


    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4


    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 2*cm, "Certificado de Residencia")
    
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, height - 4*cm, "La Junta de Vecinos de [Nombre de la Junta] certifica que:")
    

    nombre_residente = "Juan Pérez"
    p.drawString(3*cm, height - 5*cm, f"Don/Doña {nombre_residente}, R.U.N. [RUT del residente],")
    

    p.drawString(2*cm, height - 7*cm, "Reside en la dirección [Dirección completa] de la comuna de El Bosque, Santiago.")
    p.drawString(2*cm, height - 8*cm, "Se extiende este certificado para los fines que estime convenientes.")
    

    firma_virtual_path = 'C:/Users/alexa/OneDrive/Documentos/duoc/Junta de vecinos/jvv_backend/media/firma.png'
    try:
    
        p.drawImage(firma_virtual_path, 2*cm, 5*cm, width=4*cm, height=2*cm)
    except FileNotFoundError:
    
        p.drawString(2*cm, 5*cm, "Firma no disponible.")


    p.setFont("Helvetica", 10)
    p.drawString(2*cm, 4.5*cm, "______________________")
    p.drawString(2*cm, 4*cm, "Nombre del Presidente/a de la Junta de Vecinos")
    p.drawString(2*cm, 3.5*cm, "R.U.T. del Presidente/a")
    
    p.showPage()
    p.save()


    buffer.seek(0)
    

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificado_residencia.pdf"'
    
    return response




N8N_EMAIL_WEBHOOK_URL = "https://alexander14.app.n8n.cloud/webhook-test/f676843e-e967-4abf-906b-8b0ee255d291"

@csrf_exempt
def enviar_correo(request):
    if request.method == 'POST':
        data_para_n8n = {
            "to": "matiasxz14@gmail.com",
            "subject": "Correo de prueba desde Django",
            "body": "¡Este es un correo enviado usando Django y n8n!",
        }

        try:
            response = requests.post(N8N_EMAIL_WEBHOOK_URL, json=data_para_n8n)
            
            response.raise_for_status()
            
            return JsonResponse({'status': 'Correo enviado correctamente'})

        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'Error', 'message': 'Solo se permiten peticiones POST'}, status=405)


# En tu archivo views.py
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

N8N_WA_WEBHOOK_URL = "https://alexander14.app.n8n.cloud/webhook-test/7f27b483-3981-44ba-91aa-e881a81e2b1c"

@csrf_exempt
def enviar_whatsapp(request):
    if request.method == 'POST':
        data_para_n8n = {
            "to_number": "+56985083641",
            "message": "¡Hola!9899 Este es un mensaje de prueba enviado desde Django a través de n8n.",
        }

        try:
            response = requests.post(N8N_WA_WEBHOOK_URL, json=data_para_n8n)
            
            response.raise_for_status()
            
            return JsonResponse({'status': 'Mensaje de WhatsApp enviado correctamente'})

        except requests.exceptions.RequestException as e:
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'Error', 'message': 'Solo se permiten peticiones POST'}, status=405)

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import authenticate
from .models import CustomUser, JuntaVecinos, Noticia, SolicitudCertificado, Actividad
from .serializers import (UserSerializer, UserLoginSerializer, RegisterSerializer, 
                         LoginSerializer, JuntaVecinosSerializer, NoticiaSerializer,
                         SolicitudCertificadoSerializer, ActividadSerializer)
from .permissions import EsAdministrador, EsDirectivo, EsVecino, PuedeGestionarNoticias, EsVecinoOdirector

# ================= VISTAS PÚBLICAS (HTML) =================
@csrf_exempt
def index(request):
    return render(request, 'index.html')


@csrf_exempt
def eventos(request):
    return render(request, 'eventos.html')

@csrf_exempt
def contacto(request):
    return render(request, 'contacto.html')

@csrf_exempt
def mi_barrio(request):
    return render(request, 'mi_barrio.html')

@csrf_exempt
def login_view(request):
    return render(request, 'login.html')

@csrf_exempt
def registro_vecino(request):
    return render(request, 'registro.html')

@csrf_exempt
def vecino_dashboard(request):
    return render(request, 'vecino_dashboard.html')

@csrf_exempt
def directivo_dashboard(request):
    return render(request, 'directivo_dashboard.html')

@csrf_exempt
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# ================= AUTENTICACIÓN =================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    """
    Gestiona el inicio de sesión y verifica si el usuario ha sido aprobado.
    """
    serializer = LoginSerializer(data=request.data)
    
    # 1. Valida las credenciales (correo y contraseña)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # 2. VERIFICACIÓN CLAVE: Si el rol del usuario es 'registrado',
        #    significa que la cuenta está pendiente y se deniega el acceso.
        if user.rol == 'registrado':
            return Response(
                {"error": "Tu cuenta está pendiente de aprobación por la administración."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # 3. Si el rol es diferente de 'registrado' (por ejemplo, 'vecino', 'directivo', etc.),
        #    se asume que el usuario ha sido aprobado y se procede con el login.
        refresh = RefreshToken.for_user(user)
        user_serializer = UserLoginSerializer(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        })
    
    # 4. Si la validación falla (credenciales incorrectas), devuelve los errores del serializador
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registro_publico_vecino(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Registro exitoso. Esperando aprobación del administrador.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def current_user(request):
    if not request.user.is_authenticated:
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# ================= DASHBOARDS VECINO =================
@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def vecino_dashboard_api(request):
    try:
        usuario = request.user
        
        noticias = Noticia.objects.filter(
            junta_vecinos=usuario.junta_vecinos,
            es_publica=True
        ).order_by('-fecha_creacion')[:5]
        
        # Solicitudes de certificados
        solicitudes_certificados = SolicitudCertificado.objects.filter(vecino=usuario)
        
        # Solicitudes de espacios (nuevo)
        solicitudes_espacios = SolicitudEspacio.objects.filter(solicitante=usuario)
        
        # Proyectos vecinales (nuevo)
        proyectos_vecinales = ProyectoVecinal.objects.filter(proponente=usuario)
        
        actividades = Actividad.objects.filter(
            junta_vecinos=usuario.junta_vecinos,
            fecha__gte=timezone.now()
        ).order_by('fecha')[:5]
        
        data = {
            'usuario': {
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'email': usuario.email,
                'telefono': usuario.telefono,
                'direccion': usuario.direccion,
                'junta_vecinos': usuario.junta_vecinos.nombre if usuario.junta_vecinos else None
            },
            'noticias_recientes': NoticiaSerializer(noticias, many=True).data,
            'proximas_actividades': [
                {
                    'id': act.id,
                    'titulo': act.titulo,
                    'fecha': act.fecha,
                    'descripcion': act.descripcion,
                    'cupo_disponible': act.cupo_maximo - act.inscripciones.count()
                }
                for act in actividades
            ],
            'estadisticas': {
                # Certificados
                'certificados_totales': solicitudes_certificados.count(),
                'certificados_pendientes': solicitudes_certificados.filter(estado='pendiente').count(),
                'certificados_aprobados': solicitudes_certificados.filter(estado='aprobado').count(),
                
                # Espacios (nuevo)
                'espacios_totales': solicitudes_espacios.count(),
                'espacios_pendientes': solicitudes_espacios.filter(estado='pendiente').count(),
                'espacios_aprobados': solicitudes_espacios.filter(estado='aprobado').count(),
                
                # Proyectos (nuevo)
                'proyectos_totales': proyectos_vecinales.count(),
                'proyectos_pendientes': proyectos_vecinales.filter(estado='pendiente').count(),
                'proyectos_aprobados': proyectos_vecinales.filter(estado='aprobado').count(),
                'proyectos_revision': proyectos_vecinales.filter(estado='revision').count(),
                
                # Totales generales
                'solicitudes_totales': (solicitudes_certificados.count() + 
                                       solicitudes_espacios.count() + 
                                       proyectos_vecinales.count()),
                'solicitudes_pendientes_totales': (solicitudes_certificados.filter(estado='pendiente').count() +
                                                  solicitudes_espacios.filter(estado='pendiente').count() +
                                                  proyectos_vecinales.filter(estado='pendiente').count())
            }
        }
        return Response(data)
        
    except Exception as e:
        print("Ha ocurrido una excepción:", e) 

        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsAdministrador])
def admin_dashboard_api(request):
    try:
        data = {
            'total_usuarios': CustomUser.objects.filter(junta_vecinos=request.user.junta_vecinos).count(),
            'total_noticias': Noticia.objects.filter(junta_vecinos=request.user.junta_vecinos).count(),
            'solicitudes_pendientes': SolicitudCertificado.objects.filter(estado='pendiente').count(),
            'usuarios_recientes': list(CustomUser.objects.filter(
                junta_vecinos=request.user.junta_vecinos
            ).order_by('-date_joined')[:5].values('id', 'nombre', 'email', 'date_joined'))
        }
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ================= GESTIÓN DE USUARIOS =================
@api_view(['GET'])
@permission_classes([EsAdministrador])
def usuarios_por_junta(request):
    usuarios = CustomUser.objects.filter(junta_vecinos=request.user.junta_vecinos)
    serializer = UserSerializer(usuarios, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([EsAdministrador])
def aprobar_vecino(request, user_id):
    try:
        vecino = CustomUser.objects.get(id=user_id, rol='vecino', is_active=False)
        vecino.is_active = True
        vecino.junta_vecinos = request.user.junta_vecinos
        vecino.save()
        
        return Response({
            'message': f'Vecino {vecino.email} aprobado exitosamente',
            'vecino': UserSerializer(vecino).data
        })
    except CustomUser.DoesNotExist:
        return Response({'error': 'Vecino no encontrado o ya está aprobado'}, status=status.HTTP_404_NOT_FOUND)

# ================= NOTICIAS PÚBLICAS =================
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def noticias_publicas(request):
    noticias = Noticia.objects.filter(es_publica=True).order_by('-fecha_publicacion')
    serializer = NoticiaSerializer(noticias, many=True)
    return Response(serializer.data)

# ================= VISTAS BASE PARA CRUD =================
class NoticiaListCreateView(generics.ListCreateAPIView):
    serializer_class = NoticiaSerializer
    permission_classes = [permissions.IsAuthenticated, PuedeGestionarNoticias]
    
    def get_queryset(self):
        return Noticia.objects.filter(junta_vecinos=self.request.user.junta_vecinos)
    
    def perform_create(self, serializer):
        serializer.save(autor=self.request.user, junta_vecinos=self.request.user.junta_vecinos)

class NoticiaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoticiaSerializer
    permission_classes = [permissions.IsAuthenticated, PuedeGestionarNoticias]
    
    def get_queryset(self):
        return Noticia.objects.filter(junta_vecinos=self.request.user.junta_vecinos)

# ================= VISTAS VECINOS ==========================
@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def postular_proyecto(request):
    data = request.data.copy()
    # 1. Valida que el usuario tenga una junta de vecinos antes de continuar
    if not request.user.junta_vecinos:
        return Response(
            {'error': 'El usuario debe pertenecer a una junta de vecinos para postular un proyecto.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. El serializador solo necesita los datos que vienen en el cuerpo de la petición (título, descripción, etc.)
    serializer = ProyectoVecinalPostSerializer(data=data)
    
    if serializer.is_valid():
        # 3. Guarda el proyecto pasando los objetos del usuario y la junta directamente.
        # Esto asegura que los campos se llenen correctamente y evita errores de integridad.
        serializer.save(
            proponente=request.user,
            junta_vecinos=request.user.junta_vecinos
        )
        return Response({'success': 'Proyecto postulado correctamente.'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)   

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def vecino_proyectos(request):
    # Validar que el usuario tenga una junta de vecinos
    if not request.user.junta_vecinos:
        return Response(
            {'error': 'El usuario debe pertenecer a una junta de vecinos para ver sus proyectos.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # 1. Obtén el queryset
    proyectos = ProyectoVecinal.objects.filter(proponente=request.user).order_by('-fecha_creacion')

    # 2. Serializa el queryset
    serializer = ProyectoVecinalSerializer(proyectos, many=True)

    # 3. Devuelve una respuesta con los datos serializados
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def solicitar_certificado(request):
    serializer = SolicitudCertificadoSerializer(
        data=request.data, 
        context={'request': request}  # ¡Esto es importante!
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({'success': 'Solicitud enviada correctamente'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_solicitudes_certificados(request):
    solicitudes = SolicitudCertificado.objects.filter(vecino=request.user).order_by('-fecha_solicitud')
    serializer = SolicitudCertificadoSerializer(solicitudes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def listar_espacios(request):
    espacios = Espacio.objects.filter(disponible=True, junta_vecinos=request.user.junta_vecinos)
    serializer = EspacioSerializer(espacios, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def solicitar_espacio(request):
    serializer = SolicitudEspacioSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Verificar disponibilidad
        espacio_id = request.data.get('espacio')
        fecha_evento = request.data.get('fecha_evento')
        hora_inicio = request.data.get('hora_inicio')
        
        # Convertir string a objeto time
        hora_inicio_obj = datetime.strptime(hora_inicio, '%H:%M').time()
        
        existe_reserva = SolicitudEspacio.objects.filter(
            espacio_id=espacio_id,
            fecha_evento=fecha_evento,
            hora_inicio=hora_inicio_obj,
            estado__in=['pendiente', 'aprobado']
        ).exists()
        
        if existe_reserva:
            return Response(
                {'error': 'El espacio ya está reservado para esa fecha y hora'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response({'success': 'Solicitud de espacio enviada correctamente'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_solicitudes_espacio(request):
    solicitudes = SolicitudEspacio.objects.filter(
        solicitante=request.user
    ).order_by('-fecha_solicitud')
    
    serializer = SolicitudEspacioSerializer(solicitudes, many=True)
    return Response(serializer.data)




# views.py
@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def listar_actividades(request):
    print("Usuario:", request.user)
    print(request.user.rol)
    try:
        actividades = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos,
            fecha__gte=timezone.now()
        ).order_by('fecha')
        
        # Agregar información de cupos e inscripción
        actividades_data = []
        for actividad in actividades:
            inscritos_count = InscripcionActividad.objects.filter(actividad=actividad).count()
            esta_inscrito = InscripcionActividad.objects.filter(
                actividad=actividad,
                vecino=request.user
            ).exists()
            
            actividades_data.append({
                'id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'fecha': actividad.fecha,
                'cupo_maximo': actividad.cupo_maximo,
                'cupo_disponible': actividad.cupo_maximo - inscritos_count if actividad.cupo_maximo > 0 else None,
                'esta_inscrito': esta_inscrito,
                'creada_por': f"{actividad.creada_por.nombre} {actividad.creada_por.apellido}"
            })
        
        return Response(actividades_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def detalle_actividad(request, actividad_id):
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        
        inscritos_count = InscripcionActividad.objects.filter(actividad=actividad).count()
        esta_inscrito = InscripcionActividad.objects.filter(
            actividad=actividad,
            vecino=request.user
        ).exists()
        
        data = {
            'id': actividad.id,
            'titulo': actividad.titulo,
            'descripcion': actividad.descripcion,
            'fecha': actividad.fecha,
            'cupo_maximo': actividad.cupo_maximo,
            'cupo_disponible': actividad.cupo_maximo - inscritos_count if actividad.cupo_maximo > 0 else None,
            'esta_inscrito': esta_inscrito,
            'creada_por': f"{actividad.creada_por.nombre} {actividad.creada_por.apellido}"
        }
        
        return Response(data)
        
    except Actividad.DoesNotExist:
        return Response({'error': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# views.py
from django.db import IntegrityError
from django.utils import timezone

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def inscribir_actividad(request, actividad_id):
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        
        # Verificar si la actividad ya pasó
        if actividad.fecha < timezone.now():
            return Response(
                {'error': 'Esta actividad ya ha finalizado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si hay cupo disponible
        inscritos_count = InscripcionActividad.objects.filter(actividad=actividad).count()
        if actividad.cupo_maximo > 0 and inscritos_count >= actividad.cupo_maximo:
            return Response(
                {'error': 'No hay cupos disponibles para esta actividad'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya está inscrito
        if InscripcionActividad.objects.filter(actividad=actividad, vecino=request.user).exists():
            return Response(
                {'error': 'Ya estás inscrito en esta actividad'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear la inscripción
        inscripcion = InscripcionActividad.objects.create(
            actividad=actividad,
            vecino=request.user
        )
        
        return Response({
            'success': 'Inscripción realizada correctamente',
            'cupos_restantes': actividad.cupo_maximo - (inscritos_count + 1) if actividad.cupo_maximo > 0 else None
        }, status=status.HTTP_201_CREATED)
        
    except Actividad.DoesNotExist:
        print("Ha ocurrido una excepción:", IntegrityError)
        return Response({'error': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        print("Ha ocurrido una excepción:", IntegrityError)
        return Response({'error': 'Ya estás inscrito en esta actividad'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("Ha ocurrido una excepción:", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_inscripciones(request):
    try:
        inscripciones = InscripcionActividad.objects.filter(
            vecino=request.user,
            actividad__fecha__gte=timezone.now()  # Solo actividades futuras
        ).select_related('actividad').order_by('actividad__fecha')
        
        data = [
            {
                'id': insc.actividad.id,
                'titulo': insc.actividad.titulo,
                'fecha': insc.actividad.fecha,
                'descripcion': insc.actividad.descripcion,
                'fecha_inscripcion': insc.fecha_inscripcion,
                'cupo_maximo': insc.actividad.cupo_maximo,
                'inscritos_actuales': InscripcionActividad.objects.filter(actividad=insc.actividad).count()
            }
            for insc in inscripciones
        ]
        
        
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# views.py
@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_inscripciones_detalladas(request):
    try:
        # Obtener inscripciones con información detallada de las actividades
        inscripciones = InscripcionActividad.objects.filter(
            vecino=request.user
        ).select_related('actividad').order_by('-fecha_inscripcion')
        
        data = [] 
        for insc in inscripciones:
            data.append({
                'id': insc.actividad.id,
                'titulo': insc.actividad.titulo,
                'fecha': insc.actividad.fecha,
                'fecha_inscripcion': insc.fecha_inscripcion,
                'descripcion': insc.actividad.descripcion,
            })
        return Response(data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def detalle_noticia_api(request, noticia_id):
    try:
        print ("Accediendo a detalle_noticia_api con noticia_id:", noticia_id)
        noticia = Noticia.objects.get(id=noticia_id)

        
        serializer = NoticiaDetalleSerializer(noticia)
        return Response(serializer.data)
        
    except Noticia.DoesNotExist:
        return Response({'error': 'Noticia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Ha ocurrido una excepción:", e) 
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def noticias_publicas_api(request):
    """
    Vista pública para obtener todas las noticias.
    Cualquier persona puede acceder.
    """
    try:
        # Filtra solo las noticias que están marcadas como públicas
        noticias = Noticia.objects.filter(es_publica=True).order_by('-fecha_creacion')
        
        serializer = NoticiaListSerializer(noticias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error al obtener noticias públicas: {e}", exc_info=True)
        return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@parser_classes([MultiPartParser, FormParser]) # Importante: Añade esta línea
def registro_vecino_api(request):
    """
    API para el registro de nuevos vecinos.
    """
    serializer = VecinoRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Registro exitoso. Su cuenta está pendiente de aprobación por el administrador.'
        }, status=status.HTTP_201_CREATED)
    else:
        # Añade esta línea para ver los errores en la consola del servidor
        print("Errores del serializador:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([EsDirectivo])
def directivo_dashboard_api(request):
    """
    API para obtener los datos del dashboard de un directivo.
    """
    try:
        # 1. Obtener estadísticas
        total_vecinos = CustomUser.objects.filter(is_active=True).count()
        pendientes_aprobacion = CustomUser.objects.filter(rol='registrado').count()
        certificados_pendientes = SolicitudCertificado.objects.filter(estado='pendiente').count()
        eventos_activos = Actividad.objects.filter(fecha__gte=timezone.now()).count()
        
        # CAMBIO CLAVE: Obtener el conteo de proyectos pendientes
        proyectos_pendientes = ProyectoVecinal.objects.filter(estado='pendiente').count()

        # 2. Obtener listas de elementos para las tablas y tarjetas
        usuarios_pendientes = list(CustomUser.objects.filter(
            rol='registrado'
        ).values('id', 'nombre', 'apellido', 'rut', 'email', 'date_joined', 'documento_verificacion'))
        
        for user in usuarios_pendientes:
            user['nombre_completo'] = f"{user['nombre']} {user['apellido']}"
            user['fecha_registro'] = user['date_joined']
            del user['nombre']
            del user['apellido']
            del user['date_joined']

        proximos_eventos = list(Actividad.objects.filter(
            fecha__gte=timezone.now()
        ).order_by('fecha')[:5].values('id', 'titulo', 'fecha', 'descripcion'))

        noticias_recientes = list(Noticia.objects.order_by(
            '-fecha_creacion'
        )[:5].values('id', 'titulo', 'fecha_creacion', 'contenido'))

        proyectos_pendientes_lista = list(ProyectoVecinal.objects.filter(
            estado='pendiente'
        ).values(
            'id',
            'titulo',
            'proponente__nombre',   
            'fecha_creacion'       
        ))
        # 3. Obtener datos para el gráfico de solicitudes
        solicitudes_mes_a_mes = list(SolicitudCertificado.objects
            .annotate(mes_num=ExtractMonth('fecha_solicitud'))
            .values('mes_num')
            .annotate(total=Count('id'))
            .order_by('mes_num'))

        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        
        chart_data = [{'mes': meses.get(item['mes_num']), 'total': item['total']} for item in solicitudes_mes_a_mes]

        # 4. Construir la respuesta final con todos los datos
        data = {
            'total_vecinos': total_vecinos,
            'pendientes_aprobacion': pendientes_aprobacion,
            'certificados_pendientes': certificados_pendientes,
            'eventos_activos': eventos_activos,
            'proyectos_pendientes': proyectos_pendientes, 
            'proyectos_pendientes_lista': proyectos_pendientes_lista, 
            'usuarios_pendientes': usuarios_pendientes,
            'proximos_eventos': proximos_eventos,
            'noticias_recientes': noticias_recientes,
            'solicitudes_mes_a_mes': chart_data,
            'permisos': {
                'gestionar_noticias': request.user.puede_gestionar_noticias,
                'gestionar_eventos': request.user.puede_gestionar_calendario,
                'gestionar_certificados': request.user.puede_gestionar_certificados,
            }
        }
        
        return Response(data)
    
    except Exception as e:
        print(f"Error en directivo_dashboard_api: {e}")
        return Response({"error": "Ocurrió un error en el servidor."}, status=500)

@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_usuario(request, user_id):
    """
    Cambia el rol de un usuario 'registrado' a 'vecino'.
    """
    try:
        user_to_approve = CustomUser.objects.get(id=user_id, rol='registrado')
        user_to_approve.rol = 'vecino'
        user_to_approve.save()
        return Response({'message': 'Usuario aprobado correctamente.'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Usuario no encontrado o ya aprobado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([EsDirectivo])
def rechazar_usuario(request, user_id):
    """
    Cambia el rol de un usuario 'registrado' a 'rechazado'.
    """
    try:
        user_to_reject = CustomUser.objects.get(id=user_id, rol='registrado')
        user_to_reject.rol = 'rechazado'
        user_to_reject.save()
        return Response({'message': 'Usuario rechazado correctamente.'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Usuario no encontrado o ya procesado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([EsDirectivo])
@csrf_exempt  
def lista_certificados_api(request):
    """
    API para obtener la lista de solicitudes de certificados.
    Incluye los datos del usuario que la solicitó.
    """
    try:
        solicitudes = SolicitudCertificado.objects.all().order_by('-fecha_solicitud')
        
        # Formatear la respuesta
        data = []
        for s in solicitudes:
            data.append({
                'id': s.id,
                'tipo_certificado': s.tipo,
                'estado': s.estado,
                'motivo': s.motivo,
                'fecha_solicitud': s.fecha_solicitud,
                'usuario': {
                    'id': s.vecino.id,
                    'nombre_completo': f"{s.vecino.nombre} {s.vecino.apellido}",
                    'rut': s.vecino.rut,
                    'email': s.vecino.email
                }
            })
        
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error en lista_certificados_api: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/e1d296c6-c14b-451b-a1d3-2b0793e81c7b"


@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_certificado(request, certificado_id):
    """
    Aprueba una solicitud de certificado, genera un PDF y lo adjunta a la notificación de n8n.
    """
    try:
        solicitud = SolicitudCertificado.objects.get(id=certificado_id)
        
        # Validar si ya está procesada
        if solicitud.estado != 'pendiente':
            return Response({'error': 'La solicitud ya ha sido procesada.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Cambiar el estado a 'aprobado'
        solicitud.estado = 'aprobado'
        solicitud.fecha_resolucion = now()
        solicitud.resuelto_por = request.user
        #solicitud.save()
        
        # 2. Generar el PDF
        pdf_buffer = generar_certificado_pdf_vecino(solicitud.vecino, solicitud.motivo)
        
        # 3. Codificar el PDF a Base64
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        # 4. Preparar los datos para enviar a n8n
        try:
            vecino = solicitud.vecino 
            data_to_send = {
                "nombre_completo": f"{vecino.nombre} {vecino.apellido}",
                "email": vecino.email,
                "rut": vecino.rut,
                "telefono":  re.sub(r'\D', '', vecino.telefono),
                "certificado_base64": pdf_base64  # Añadimos el PDF codificado
            }

            # 5. Enviar la petición a n8n
            requests.post(
                N8N_WEBHOOK_URL,
                data=json.dumps(data_to_send),
                headers={'Content-Type': 'application/json'},
                timeout=0.1
            )
        except Exception as e:
            print(f"Error al enviar notificación a n8n: {e}")
            
        return Response({'message': 'Solicitud de certificado aprobada y notificación enviada.'}, status=status.HTTP_200_OK)

    except SolicitudCertificado.DoesNotExist:
        return Response({'error': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f"Ocurrió un error al procesar la solicitud: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([EsDirectivo])
def rechazar_certificado(request, certificado_id):
    """
    Rechaza una solicitud de certificado.
    """
    try:
        solicitud = SolicitudCertificado.objects.get(id=certificado_id)
        if solicitud.estado != 'pendiente':
            return Response({'error': 'La solicitud ya ha sido procesada.'}, status=status.HTTP_400_BAD_REQUEST)

        solicitud.estado = 'rechazado'
        solicitud.save()
        
        return Response({'message': 'Solicitud de certificado rechazada.'}, status=status.HTTP_200_OK)

    except SolicitudCertificado.DoesNotExist:
        return Response({'error': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def directivo_listar_usuarios(request):

    queryset = CustomUser.objects.all()

    search_query = request.query_params.get('search', None)
    if search_query is not None:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query) | 
            Q(apellido__icontains=search_query) |
            Q(rut__icontains=search_query)
        )

    # Lógica de filtro por rol
    rol_query = request.query_params.get('rol', None)
    if rol_query is not None:
        queryset = queryset.filter(rol=rol_query)

    serializer = CustomUserSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([EsDirectivo])
def directivo_editar_usuario(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DirectivoUserSerializer(user)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = DirectivoUserSerializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            # Esta línea se encarga de guardar el cambio, sea activación o desactivación.
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([EsDirectivo])
def proyectos_lista_api(request):
    try:
        proyectos = ProyectoVecinal.objects.all().order_by('-fecha_creacion')
        
        data = [{
            'id': proyecto.id,
            'titulo': proyecto.titulo,
            'descripcion': proyecto.descripcion,
            'solicitante_nombre': proyecto.proponente.get_full_name() if proyecto.proponente else 'N/A', # Usamos get_full_name()
            'fecha_creacion': proyecto.fecha_creacion.strftime('%d-%m-%Y %H:%M'),
            'estado': proyecto.estado, # Añadimos el estado
            'fecha_resolucion': proyecto.fecha_revision.strftime('%d-%m-%Y %H:%M') if proyecto.fecha_revision else 'N/A', # Fecha de resolución
            'revisado_por': proyecto.revisado_por.get_full_name() if proyecto.revisado_por else 'N/A', # Quién lo revisó
        } for proyecto in proyectos]

        return Response(data)
    except Exception as e:
        error_info = traceback.format_exc()
        print(f"Error en proyectos_lista_api: {error_info}")
        return JsonResponse({'error': str(e)}, status=500)

N8N_WEBHOOK_URL_PROYECTOVECINAL = 'http://localhost:5678/webhook/bb27b5d2-4f46-400b-b01b-f24001de5847'
def _enviar_webhook_a_n8n(proyecto, tipo_accion, user):
    """Función auxiliar para enviar el webhook."""
    payload = {
        'tipo_accion': tipo_accion,
        'proyecto_id': proyecto.id,
        'proyecto_titulo': proyecto.titulo,
        'proponente_email': proyecto.proponente.email,
        'proponente_nombre': proyecto.proponente.get_full_name(),
        'fecha_resolucion': proyecto.fecha_revision.strftime('%Y-%m-%d %H:%M:%S'),
        'revisado_por_nombre': user.get_full_name(),
    }
    try:
        requests.post(N8N_WEBHOOK_URL_PROYECTOVECINAL, json=payload, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el webhook a n8n: {e}")

@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoVecinal, pk=proyecto_id)
    proyecto.fecha_revision = timezone.now()
    proyecto.revisado_por = request.user
    
    try:

        proyecto.save()
        _enviar_webhook_a_n8n(proyecto, 'aprobacion', request.user)
        return Response({'message': 'Proyecto aprobado y webhook enviado.'})
    except IntegrityError as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([EsDirectivo])
def rechazar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoVecinal, pk=proyecto_id)
    proyecto.fecha_revision = timezone.now()
    proyecto.revisado_por = request.user
    
    try:
        proyecto.save()
        _enviar_webhook_a_n8n(proyecto, 'rechazo', request.user)
        return Response({'message': 'Proyecto rechazado y webhook enviado.'})
    except IntegrityError as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def proyecto_detalle_api(request, proyecto_id):
    try:
        proyecto = get_object_or_404(ProyectoVecinal, pk=proyecto_id)
        
        proponente_nombre = proyecto.proponente.get_full_name() if proyecto.proponente else 'N/A'

        data = {
            'id': proyecto.id,
            'titulo': proyecto.titulo,
            'descripcion': proyecto.descripcion,
            'proponente_nombre': proponente_nombre,
            'fecha_creacion': proyecto.fecha_creacion.strftime('%d-%m-%Y %H:%M'),
            'estado': proyecto.estado,
        }
        
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


N8N_WEBHOOK_URL_AVISOS = 'http://localhost:5678/webhook-test/6a6dc069-8dbe-4c3f-8f88-e5d4a330b4e2'
@api_view(['POST'])
@permission_classes([EsDirectivo])
def enviar_aviso_masivo(request):
    """
    Recibe un aviso, obtiene los datos de los usuarios 'vecino' activos
    y los envía a n8n para su distribución.
    """
    # Filtramos por rol 'vecino' y usuarios activos
    usuarios = CustomUser.objects.filter(rol='vecino', is_active=True)

    # Creando listas de emails y teléfonos
    # Usamos una lista de comprensión para asegurarnos que los campos no estén vacíos
    emails = [u.email for u in usuarios if u.email]
    telefonos = [u.telefono for u in usuarios if u.telefono]

    # Convertir las listas en cadenas de texto separadas por comas
    emails_str = ','.join(emails)
    telefonos_str = ','.join(telefonos)

    titulo = request.data.get('titulo')
    contenido = request.data.get('contenido')
    tipo_aviso = request.data.get('tipo_aviso') # 'email', 'whatsapp', o 'ambos'

    if tipo_aviso not in ['email', 'whatsapp', 'ambos']:
        return Response({'error': 'Tipo de aviso inválido'}, status=400)

    if not all([titulo, contenido, tipo_aviso]):
        return Response({'error': 'Faltan campos requeridos'}, status=400)

    payload = {
        'titulo': titulo,
        'contenido': contenido,
        'tipo_aviso': tipo_aviso,
        'emails_destino': emails_str,
        'telefonos_destino': telefonos_str,
    }

    try:
        requests.post(N8N_WEBHOOK_URL_AVISOS, json=payload, timeout=5)
        return Response({'message': 'Aviso enviado para su distribución.'})
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el webhook de aviso a n8n: {e}")
        return Response({'message': 'Aviso recibido, pero hubo un error al enviar el webhook de distribución.'}, status=500)

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

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])  # ← AÑADE PATCH AQUÍ
def noticia_detail_update_delete(request, pk):
    user = request.user
    
    try:
        noticia = Noticia.objects.get(pk=pk, junta_vecinos=user.junta_vecinos)
    except Noticia.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = NoticiaDetalleSerializer(noticia)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:  # ← ACTUALIZA ESTA LÍNEA
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
    """
    Sube una o varias imágenes a una noticia.
    """
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
    """
    Elimina una imagen de una noticia por su ID.
    """
    try:
        imagen = NoticiaImagen.objects.get(id=pk)
    except NoticiaImagen.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    imagen.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PATCH'])
@permission_classes([EsDirectivo])
def set_imagen_principal(request, pk):
    """
    Establece una imagen como principal para una noticia
    """
    try:
        noticia = Noticia.objects.get(pk=pk, junta_vecinos=request.user.junta_vecinos)
    except Noticia.DoesNotExist:
        return Response({'error': 'Noticia no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    imagen_principal_id = request.data.get('imagen_principal')
    
    if not imagen_principal_id:
        return Response({'error': 'ID de imagen principal es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    # Verificar que la imagen pertenece a esta noticia
    try:
        imagen = NoticiaImagen.objects.get(id=imagen_principal_id, noticia=noticia)
    except NoticiaImagen.DoesNotExist:
        return Response({'error': 'La imagen no pertenece a esta noticia'}, status=status.HTTP_400_BAD_REQUEST)

    # Actualizar la imagen principal - FORMA DIRECTA
    noticia.imagen_principal_id = imagen_principal_id  # Usa el ID directamente
    noticia.save()

    # Respuesta simple y segura
    return Response({
        'success': True,
        'message': 'Imagen principal actualizada correctamente',
        'imagen_principal_id': imagen_principal_id
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_reservas(request):
    """
    Obtiene todas las reservas del usuario actual
    """
    try:
        # Obtener reservas del usuario actual
        reservas = SolicitudEspacio.objects.filter(
            solicitante=request.user
        ).select_related('espacio').order_by('-fecha_solicitud')
        
        # Serializar datos
        reservas_data = []
        for reserva in reservas:
            reservas_data.append({
                'id': reserva.id,
                'espacio_id': reserva.espacio.id,
                'espacio_nombre': reserva.espacio.nombre,
                'espacio_tipo': reserva.espacio.get_tipo_display(),
                'fecha_solicitud': reserva.fecha_solicitud,
                'fecha_evento': reserva.fecha_evento,
                'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
                'hora_fin': reserva.hora_fin.strftime('%H:%M'),
                'motivo': reserva.motivo,
                'estado': reserva.estado,
                'observaciones': reserva.observaciones,
                'aprobado_por': reserva.aprobado_por.get_full_name() if reserva.aprobado_por else None
            })
        
        return Response(reservas_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener reservas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def disponibilidad_espacios(request):
    """
    Verifica la disponibilidad de horas para un espacio y fecha específicos.
    Este endpoint alimenta los select de horarios en el formulario de reserva.
    """
    espacio_id = request.GET.get('espacio_id')
    fecha_str = request.GET.get('fecha')

    if not espacio_id or not fecha_str:
        return Response(
            {'error': 'Los parámetros espacio_id y fecha son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        espacio = Espacio.objects.get(pk=espacio_id)
    except (ValueError, Espacio.DoesNotExist):
        return Response({'error': 'Datos inválidos'}, status=status.HTTP_400_BAD_REQUEST)

    reservas_del_dia = SolicitudEspacio.objects.filter(
        espacio=espacio,
        fecha_evento=fecha,
        estado__in=['aprobado', 'pendiente']
    )

    all_hours = [time(hour, 0) for hour in range(8, 21)]
    unavailable_hours = set()

    for reserva in reservas_del_dia:
        # Crea un conjunto de las horas ocupadas por cada reserva.
        start_hour = reserva.hora_inicio.hour
        end_hour = reserva.hora_fin.hour
        for hour in range(start_hour, end_hour):
            unavailable_hours.add(time(hour, 0))

    available_hours = [h.strftime('%H:%M') for h in all_hours if h not in unavailable_hours]
    
    return Response({
        'espacio_id': espacio_id,
        'fecha': fecha_str,
        'available_hours': available_hours,
        'unavailable_hours': [h.strftime('%H:%M') for h in unavailable_hours],
    })

@api_view(['GET'])
@permission_classes([EsDirectivo])
def todas_reservas(request):
    """
    Obtiene todas las reservas de la junta de vecinos (para directivos)
    """
    try:
        # Obtener todas las reservas de la junta
        reservas = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=request.user.junta_vecinos
        ).select_related('espacio', 'solicitante').order_by('-fecha_solicitud')
        
        reservas_data = []
        for reserva in reservas:
            reservas_data.append({
                'id': reserva.id,
                'espacio_nombre': reserva.espacio.nombre,
                'solicitante_nombre': reserva.solicitante.get_full_name(),
                'solicitante_email': reserva.solicitante.email,
                'fecha_solicitud': reserva.fecha_solicitud,
                'fecha_evento': reserva.fecha_evento,
                'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
                'hora_fin': reserva.hora_fin.strftime('%H:%M'),
                'motivo': reserva.motivo,
                'estado': reserva.estado,
                'observaciones': reserva.observaciones,
                'aprobado_por': reserva.aprobado_por.get_full_name() if reserva.aprobado_por else None
            })
        
        return Response(reservas_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener reservas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def lista_espacios(request):
    """
    Obtiene todos los espacios disponibles de la junta de vecinos
    """
    try:
        espacios = Espacio.objects.filter(
            junta_vecinos=request.user.junta_vecinos,
            disponible=True
        )
        
        espacios_data = []
        for espacio in espacios:
            espacios_data.append({
                'id': espacio.id,
                'nombre': espacio.nombre,
                'tipo': espacio.tipo,
                'tipo_display': espacio.get_tipo_display(),
                'descripcion': espacio.descripcion,
                'capacidad': getattr(espacio, 'capacidad', 'N/A')  # Si tu modelo tiene capacidad
            })
        
        return Response(espacios_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener espacios: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def reservas_lista(request):
    user = request.user
    if not user.junta_vecinos:
        return Response({'error': 'El usuario no pertenece a una junta de vecinos'}, status=status.HTTP_403_FORBIDDEN)

    reservas = SolicitudEspacio.objects.filter(
        espacio__junta_vecinos=user.junta_vecinos,
        estado__in=['aprobado', 'pendiente']
    ).select_related('espacio', 'solicitante') # Optimización para evitar consultas N+1

    serializer = SolicitudEspacioSerializer(reservas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def detalles_dia(request):
    """
    Obtiene los detalles completos de las reservas para un espacio y fecha específicos.
    Este endpoint es utilizado por el modal para mostrar la información detallada.
    """
    espacio_id = request.GET.get('espacio_id')
    fecha_str = request.GET.get('fecha')

    if not espacio_id or not fecha_str:
        return Response(
            {'error': 'Los parámetros espacio_id y fecha son requeridos.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Formato de fecha inválido. Use AAAA-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Filtra las reservas por el espacio, la fecha y el estado
    reservas_del_dia = SolicitudEspacio.objects.filter(
        espacio_id=espacio_id,
        fecha_evento=fecha,
        estado__in=['aprobado', 'pendiente']
    ).order_by('hora_inicio') # Ordena por la hora de inicio

    # Serializa los datos para enviarlos como respuesta JSON
    serializer = SolicitudEspacioSerializer(reservas_del_dia, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import SolicitudEspacio, Espacio
from .permissions import EsDirectivo

@api_view(['GET'])
@permission_classes([EsDirectivo])
def todas_solicitudes_espacios(request):
    """
    Obtiene todas las solicitudes de espacios de la junta de vecinos
    con filtros opcionales.
    """
    try:
        # Obtener parámetros de filtro
        estado = request.GET.get('estado')
        espacio_id = request.GET.get('espacio')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        # Base query: todas las solicitudes de la junta de vecinos
        solicitudes = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=request.user.junta_vecinos
        ).select_related('espacio', 'solicitante', 'aprobado_por').order_by('-fecha_solicitud')
        
        # Aplicar filtros
        if estado:
            solicitudes = solicitudes.filter(estado=estado)
        
        if espacio_id:
            solicitudes = solicitudes.filter(espacio_id=espacio_id)
        
        if fecha_desde:
            solicitudes = solicitudes.filter(fecha_solicitud__date__gte=fecha_desde)
        
        if fecha_hasta:
            solicitudes = solicitudes.filter(fecha_solicitud__date__lte=fecha_hasta)
        
        # Serializar datos
        solicitudes_data = []
        for solicitud in solicitudes:
            solicitudes_data.append({
                'id': solicitud.id,
                'solicitante_id': solicitud.solicitante.id,
                'solicitante_nombre': solicitud.solicitante.get_full_name(),
                'solicitante_email': solicitud.solicitante.email,
                'solicitante_telefono': solicitud.solicitante.telefono,
                'espacio_id': solicitud.espacio.id,
                'espacio_nombre': solicitud.espacio.nombre,
                'fecha_solicitud': solicitud.fecha_solicitud,
                'fecha_evento': solicitud.fecha_evento,
                'hora_inicio': solicitud.hora_inicio.strftime('%H:%M'),
                'hora_fin': solicitud.hora_fin.strftime('%H:%M'),
                'motivo': solicitud.motivo,
                'estado': solicitud.estado,
                'observaciones': solicitud.observaciones,
                'aprobado_por': solicitud.aprobado_por.get_full_name() if solicitud.aprobado_por else None,
                'aprobado_por_id': solicitud.aprobado_por.id if solicitud.aprobado_por else None
            })
        
        return Response(solicitudes_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener solicitudes: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsDirectivo])
def detalle_solicitud_espacio(request, pk):
    """
    Obtiene el detalle completo de una solicitud de espacio específica
    """
    try:
        # Obtener la solicitud específica de la junta de vecinos
        solicitud = SolicitudEspacio.objects.select_related(
            'espacio', 'solicitante', 'aprobado_por'
        ).get(
            id=pk,
            espacio__junta_vecinos=request.user.junta_vecinos
        )
        
        # Serializar datos completos
        solicitud_data = {
            'id': solicitud.id,
            'solicitante': {
                'id': solicitud.solicitante.id,
                'nombre_completo': f"{solicitud.solicitante.nombre} {solicitud.solicitante.apellido}",
                'email': solicitud.solicitante.email,
                'telefono': solicitud.solicitante.telefono,
                'direccion': solicitud.solicitante.direccion,
                'rut': solicitud.solicitante.rut
            },
            'espacio': {
                'id': solicitud.espacio.id,
                'nombre': solicitud.espacio.nombre,
                'tipo': solicitud.espacio.tipo,
                'tipo_display': solicitud.espacio.get_tipo_display(),
                'descripcion': solicitud.espacio.descripcion
            },
            'fecha_solicitud': solicitud.fecha_solicitud,
            'fecha_evento': solicitud.fecha_evento,
            'hora_inicio': solicitud.hora_inicio.strftime('%H:%M'),
            'hora_fin': solicitud.hora_fin.strftime('%H:%M'),
            'motivo': solicitud.motivo,
            'estado': solicitud.estado,
            'observaciones': solicitud.observaciones,
            'aprobado_por': {
                'id': solicitud.aprobado_por.id if solicitud.aprobado_por else None,
                'nombre': f"{solicitud.aprobado_por.nombre} {solicitud.aprobado_por.apellido}" if solicitud.aprobado_por else None
            } if solicitud.aprobado_por else None
        }
        
        return Response(solicitud_data, status=status.HTTP_200_OK)
        
    except SolicitudEspacio.DoesNotExist:
        return Response(
            {'error': 'Solicitud no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al obtener detalle: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_solicitud_espacio(request, pk):
    """
    Aprueba una solicitud de espacio
    """
    try:
        # Obtener la solicitud
        solicitud = SolicitudEspacio.objects.get(
            id=pk,
            espacio__junta_vecinos=request.user.junta_vecinos,
            estado='pendiente'  # Solo se pueden aprobar solicitudes pendientes
        )
        
        # Verificar que no haya conflictos de horario
        conflicto = SolicitudEspacio.objects.filter(
            espacio=solicitud.espacio,
            fecha_evento=solicitud.fecha_evento,
            hora_inicio__lt=solicitud.hora_fin,
            hora_fin__gt=solicitud.hora_inicio,
            estado='aprobado'
        ).exclude(id=pk).exists()
        
        if conflicto:
            return Response(
                {'error': 'Ya existe una reserva aprobada en ese horario'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aprobar la solicitud
        solicitud.estado = 'aprobado'
        solicitud.aprobado_por = request.user
        solicitud.observaciones = request.data.get('observaciones', '')
        solicitud.save()
        
        # TODO: Enviar email de confirmación al solicitante
        
        return Response(
            {'message': 'Solicitud aprobada correctamente'},
            status=status.HTTP_200_OK
        )
        
    except SolicitudEspacio.DoesNotExist:
        return Response(
            {'error': 'Solicitud no encontrada o ya no está pendiente'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al aprobar solicitud: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([EsDirectivo])
def rechazar_solicitud_espacio(request, pk):
    """
    Rechaza una solicitud de espacio
    """
    try:
        # Obtener la solicitud
        solicitud = SolicitudEspacio.objects.get(
            id=pk,
            espacio__junta_vecinos=request.user.junta_vecinos,
            estado='pendiente'  # Solo se pueden rechazar solicitudes pendientes
        )
        
        # Validar que venga el motivo
        motivo = request.data.get('motivo')
        if not motivo or not motivo.strip():
            return Response(
                {'error': 'El motivo del rechazo es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rechazar la solicitud
        solicitud.estado = 'rechazado'
        solicitud.aprobado_por = request.user
        solicitud.observaciones = f"Rechazado: {motivo.strip()}"
        solicitud.save()
        
        # TODO: Enviar email de rechazo al solicitante
        
        return Response(
            {'message': 'Solicitud rechazada correctamente'},
            status=status.HTTP_200_OK
        )
        
    except SolicitudEspacio.DoesNotExist:
        return Response(
            {'error': 'Solicitud no encontrada o ya no está pendiente'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al rechazar solicitud: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsDirectivo])
def estadisticas_espacios(request):
    """
    Obtiene estadísticas de uso de espacios (compatible con SQLite)
    """
    try:
        junta_vecinos = request.user.junta_vecinos
        
        # Estadísticas básicas
        total_solicitudes = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=junta_vecinos
        ).count()
        
        solicitudes_pendientes = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=junta_vecinos,
            estado='pendiente'
        ).count()
        
        solicitudes_aprobadas = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=junta_vecinos,
            estado='aprobado'
        ).count()
        
        solicitudes_rechazadas = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=junta_vecinos,
            estado='rechazado'
        ).count()
        
        # Solicitudes por mes (últimos 6 meses) - Compatible con SQLite
        seis_meses_atras = timezone.now() - timezone.timedelta(days=180)
        
        # Usamos ExtractYear y ExtractMonth de Django para compatibilidad
        from django.db.models.functions import ExtractYear, ExtractMonth
        
        solicitudes_mes_a_mes = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=junta_vecinos,
            fecha_solicitud__gte=seis_meses_atras
        ).annotate(
            year=ExtractYear('fecha_solicitud'),
            month=ExtractMonth('fecha_solicitud')
        ).values('year', 'month').annotate(
            total=Count('id'),
            aprobadas=Count('id', filter=Q(estado='aprobado')),
            pendientes=Count('id', filter=Q(estado='pendiente')),
            rechazadas=Count('id', filter=Q(estado='rechazado'))
        ).order_by('year', 'month')
        
        # Formatear los datos de mes a mes
        solicitudes_mes_formateadas = []
        for item in solicitudes_mes_a_mes:
            fecha = timezone.datetime(year=item['year'], month=item['month'], day=1)
            solicitudes_mes_formateadas.append({
                'mes': fecha.strftime('%Y-%m'),
                'total': item['total'],
                'aprobadas': item['aprobadas'],
                'pendientes': item['pendientes'],
                'rechazadas': item['rechazadas']
            })
        
        # Espacios más populares
        espacios_populares = Espacio.objects.filter(
            junta_vecinos=junta_vecinos
        ).annotate(
            total_solicitudes=Count('solicitudespacio'),
            solicitudes_aprobadas=Count('solicitudespacio', filter=Q(solicitudespacio__estado='aprobado'))
        ).annotate(
            tasa_aprobacion=Case(
                When(total_solicitudes=0, then=Value(0.0)),
                default=ExpressionWrapper(
                    F('solicitudes_aprobadas') * 100.0 / F('total_solicitudes'),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        ).order_by('-total_solicitudes')[:5]
        
        # Serializar datos
        estadisticas = {
            'totales': {
                'solicitudes': total_solicitudes,
                'pendientes': solicitudes_pendientes,
                'aprobadas': solicitudes_aprobadas,
                'rechazadas': solicitudes_rechazadas
            },
            'solicitudes_mes_a_mes': solicitudes_mes_formateadas,
            'espacios_populares': [
                {
                    'id': espacio.id,
                    'nombre': espacio.nombre,
                    'total_solicitudes': espacio.total_solicitudes,
                    'solicitudes_aprobadas': espacio.solicitudes_aprobadas,
                    'tasa_aprobacion': round(espacio.tasa_aprobacion, 2)
                }
                for espacio in espacios_populares
            ],
            'distribucion_estados': {
                'aprobado': solicitudes_aprobadas,
                'pendiente': solicitudes_pendientes,
                'rechazado': solicitudes_rechazadas
            }
        }
        
        return Response(estadisticas, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error en estadísticas: {str(e)}")
        return Response(
            {'error': f'Error al obtener estadísticas: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET'])
@permission_classes([EsDirectivo])
def lista_espacios_directivo(request):
    """
    Obtiene todos los espacios de la junta de vecinos para directivos
    """
    try:
        espacios = Espacio.objects.filter(
            junta_vecinos=request.user.junta_vecinos,
            disponible=True
        ).order_by('nombre')
        
        espacios_data = []
        for espacio in espacios:
            # Obtener estadísticas del espacio
            total_solicitudes = SolicitudEspacio.objects.filter(
                espacio=espacio
            ).count()
            
            solicitudes_aprobadas = SolicitudEspacio.objects.filter(
                espacio=espacio,
                estado='aprobado'
            ).count()
            
            espacios_data.append({
                'id': espacio.id,
                'nombre': espacio.nombre,
                'tipo': espacio.tipo,
                'tipo_display': espacio.get_tipo_display(),
                'descripcion': espacio.descripcion,
                'disponible': espacio.disponible,
                'total_solicitudes': total_solicitudes,
                'solicitudes_aprobadas': solicitudes_aprobadas,
                'tasa_aprobacion': round((solicitudes_aprobadas / total_solicitudes * 100), 2) if total_solicitudes > 0 else 0
            })
        
        return Response(espacios_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener espacios: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def lista_eventos_vecino(request):
    """
    Obtiene todos los eventos de la junta de vecinos para vecinos
    """
    try:
        actividades = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos
        ).order_by('fecha')
        
        actividades_data = []
        for actividad in actividades:
            # Verificar si el usuario está inscrito
            esta_inscrito = InscripcionActividad.objects.filter(
                actividad=actividad,
                vecino=request.user
            ).exists()
            
            # Obtener inscripción del usuario si existe
            mi_inscripcion = None
            if esta_inscrito:
                inscripcion = InscripcionActividad.objects.get(
                    actividad=actividad,
                    vecino=request.user
                )
                mi_inscripcion = {
                    'id': inscripcion.id,
                    'cantidad_acompanantes': inscripcion.cantidad_acompanantes,
                    'nombres_acompanantes': inscripcion.nombres_acompanantes,
                    'fecha_inscripcion': inscripcion.fecha_inscripcion
                }
            
            actividades_data.append({
                'id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'fecha': actividad.fecha,
                'cupo_maximo': actividad.cupo_maximo,
                'cupo_por_vecino': actividad.cupo_por_vecino,
                'permite_acompanantes': actividad.permite_acompanantes,
                'cupos_disponibles': actividad.cupos_disponibles,
                'esta_inscrito': esta_inscrito,
                'mi_inscripcion': mi_inscripcion,
                'creada_por': {
                    'id': actividad.creada_por.id,
                    'nombre': actividad.creada_por.get_full_name()
                }
            })
        
        return Response(actividades_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error al obtener eventos: {str(e)}")
        return Response(
            {'error': f'Error al obtener eventos: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def inscribir_evento(request, evento_id):
    """
    Inscribe a un vecino en un evento con acompañantes
    """
    try:
        actividad = Actividad.objects.get(id=evento_id, junta_vecinos=request.user.junta_vecinos)
        
        cantidad_acompanantes = request.data.get('cantidad_acompanantes', 0)
        nombres_acompanantes = request.data.get('nombres_acompanantes', [])
        
        # TOTAL de personas: 1 (vecino) + acompañantes
        total_personas = 1 + cantidad_acompanantes
        
        # Validar si puede inscribirse (considerando el total de personas)
        puede_inscribirse, mensaje = actividad.puede_inscribirse(request.user, cantidad_acompanantes)
        if not puede_inscribirse:
            return Response(
                {'error': mensaje},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que los nombres coincidan con la cantidad
        if cantidad_acompanantes > 0 and len(nombres_acompanantes) != cantidad_acompanantes:
            return Response(
                {'error': 'La cantidad de nombres de acompañantes no coincide con la cantidad especificada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear la inscripción
        inscripcion = InscripcionActividad(
            actividad=actividad,
            vecino=request.user,
            cantidad_acompanantes=cantidad_acompanantes,
            nombres_acompanantes=nombres_acompanantes
        )
        inscripcion.save()
        
        return Response({
            'message': 'Inscripción exitosa',
            'total_personas': total_personas,
            'cupos_restantes': actividad.cupos_disponibles,
            'inscripcion': {
                'id': inscripcion.id,
                'cantidad_acompanantes': inscripcion.cantidad_acompanantes,
                'nombres_acompanantes': inscripcion.nombres_acompanantes,
                'fecha_inscripcion': inscripcion.fecha_inscripcion,
                'total_personas': inscripcion.total_personas
            }
        }, status=status.HTTP_201_CREATED)
        
    except Actividad.DoesNotExist:
        return Response(
            {'error': 'Evento no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error al inscribirse: {str(e)}")
        return Response(
            {'error': f'Error al inscribirse: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([EsVecinoOdirector])
def cancelar_inscripcion(request, actividad_id):
    """
    Cancela la inscripción de un vecino en un evento
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id, junta_vecinos=request.user.junta_vecinos)
        inscripcion = InscripcionActividad.objects.get(actividad=actividad, vecino=request.user)
        inscripcion.delete()
        
        return Response(
            {'message': 'Inscripción cancelada correctamente'},
            status=status.HTTP_200_OK
        )
        
    except Actividad.DoesNotExist:
        return Response(
            {'error': 'Evento no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except InscripcionActividad.DoesNotExist:
        return Response(
            {'error': 'No estás inscrito en este evento'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al cancelar inscripción: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_inscripciones(request):
    """
    Obtiene todas las inscripciones del vecino actual
    """
    try:
        inscripciones = InscripcionActividad.objects.filter(
            vecino=request.user
        ).select_related('actividad').order_by('actividad__fecha')
        
        inscripciones_data = []
        for inscripcion in inscripciones:
            actividad = inscripcion.actividad
            fecha_evento = actividad.fecha
            ahora = timezone.now()
            puede_cancelar = fecha_evento > ahora
            
            inscripciones_data.append({
                'id': inscripcion.id,
                'evento_id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'fecha_evento': actividad.fecha,
                'fecha_inscripcion': inscripcion.fecha_inscripcion,
                'cantidad_acompanantes': inscripcion.cantidad_acompanantes,
                'nombres_acompanantes': inscripcion.nombres_acompanantes,
                'total_personas': inscripcion.total_personas,
                'puede_cancelar': puede_cancelar,
                'es_hoy': fecha_evento.date() == ahora.date(),
                'estado': 'Activa' if puede_cancelar else 'Finalizada'
            })
        
        return Response(inscripciones_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener inscripciones: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# views.py (continuación)
@api_view(['GET'])
@permission_classes([EsDirectivo])
def lista_eventos_directivo(request):
    """
    Obtiene todos los eventos de la junta de vecinos para directivos
    con estadísticas detalladas
    """
    try:
        actividades = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos
        ).order_by('fecha')
        
        actividades_data = []
        for actividad in actividades:
            # Obtener estadísticas de inscripciones
            inscripciones = actividad.inscripciones.all()
            total_inscritos = sum(insc.cantidad_acompanantes + 1 for ins in inscripciones)
            total_inscripciones = inscripciones.count()
            
            actividades_data.append({
                'id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'fecha': actividad.fecha,
                'cupo_maximo': actividad.cupo_maximo,
                'cupo_por_vecino': actividad.cupo_por_vecino,
                'permite_acompanantes': actividad.permite_acompanantes,
                'cupos_disponibles': actividad.cupos_disponibles,
                'total_inscripciones': total_inscripciones,
                'total_personas_inscritas': total_inscritos,
                'tasa_ocupacion': round((total_inscritos / actividad.cupo_maximo * 100), 2) if actividad.cupo_maximo > 0 else 100,
                'creada_por': {
                    'id': actividad.creada_por.id,
                    'nombre': actividad.creada_por.get_full_name()
                },
                'inscripciones': [
                    {
                        'vecino': ins.vecino.get_full_name(),
                        'cantidad_acompanantes': ins.cantidad_acompanantes,
                        'nombres_acompanantes': ins.nombres_acompanantes,
                        'fecha_inscripcion': ins.fecha_inscripcion
                    }
                    for ins in inscripciones
                ]
            })
        
        return Response(actividades_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener eventos: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([EsDirectivo])
def detalle_evento_directivo(request, evento_id):
    """
    Obtiene detalles completos de un evento para directivos
    """
    try:
        actividad = Actividad.objects.get(
            id=evento_id,
            junta_vecinos=request.user.junta_vecinos
        )
        
        inscripciones = actividad.inscripciones.all().select_related('vecino')
        total_inscritos = sum(insc.cantidad_acompanantes + 1 for insc in inscripciones)
        
        evento_data = {
            'id': actividad.id,
            'titulo': actividad.titulo,
            'descripcion': actividad.descripcion,
            'fecha': actividad.fecha,
            'cupo_maximo': actividad.cupo_maximo,
            'cupo_por_vecino': actividad.cupo_por_vecino,
            'permite_acompanantes': actividad.permite_acompanantes,
            'cupos_disponibles': actividad.cupos_disponibles,
            'total_inscripciones': inscripciones.count(),
            'total_personas_inscritas': total_inscritos,
            'tasa_ocupacion': round((total_inscritos / actividad.cupo_maximo * 100), 2) if actividad.cupo_maximo > 0 else 100,
            'creada_por': {
                'id': actividad.creada_por.id,
                'nombre': actividad.creada_por.get_full_name(),
                'email': actividad.creada_por.email
            },
            'lista_asistencia': [
                {
                    'vecino_id': insc.vecino.id,
                    'vecino_nombre': insc.vecino.get_full_name(),
                    'vecino_rut': insc.vecino.rut,
                    'vecino_telefono': insc.vecino.telefono,
                    'cantidad_acompanantes': insc.cantidad_acompanantes,
                    'nombres_acompanantes': insc.nombres_acompanantes,
                    'total_personas': insc.total_personas,
                    'fecha_inscripcion': insc.fecha_inscripcion
                }
                for insc in inscripciones
            ]
        }
        
        return Response(evento_data, status=status.HTTP_200_OK)
        
    except Actividad.DoesNotExist:
        return Response(
            {'error': 'Evento no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error al obtener detalles del evento: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from .models import Actividad, InscripcionActividad
from .serializers import ActividadSerializer, InscripcionActividadSerializer
from .permissions import EsDirectivo
from datetime import timedelta
import csv
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import Actividad
from .serializers import ActividadSerializer
from .permissions import EsDirectivo


@api_view(['GET'])
@permission_classes([EsDirectivo])
def lista_eventos_directivo(request):
    """
    Lista todos los eventos de la junta de vecinos del directivo con filtros y estadísticas.
    """
    try:
        eventos = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos
        ).order_by('-fecha')

        # Filtros
        search = request.GET.get('search', '')
        estado = request.GET.get('estado', '')

        if search:
            eventos = eventos.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search)
            )

        if estado:
            ahora = timezone.now()
            if estado == 'activos':
                eventos = eventos.filter(fecha__gte=ahora)
            elif estado == 'pasados':
                eventos = eventos.filter(fecha__lt=ahora)
            elif estado == 'proximos':
                eventos = eventos.filter(fecha__gt=ahora)
            elif estado == 'hoy':
                eventos = eventos.filter(fecha__date=ahora.date())

        serializer = ActividadSerializer(eventos, many=True, context={'request': request})

        # Estadísticas
        ahora = timezone.now()
        total_eventos = eventos.count()
        proximos_eventos = eventos.filter(fecha__gt=ahora).count()
        eventos_hoy = eventos.filter(fecha__date=ahora.date()).count()

        total_personas_inscritas = sum(
            (1 + inscripcion.cantidad_acompanantes)
            for evento in eventos
            for inscripcion in evento.inscripciones.all()
        )

        data = {
            'eventos': serializer.data,
            'estadisticas': {
                'total_eventos': total_eventos,
                'proximos_eventos': proximos_eventos,
                'eventos_hoy': eventos_hoy,
                'total_personas_inscritas': total_personas_inscritas
            }
        }
        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error al obtener eventos: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([EsDirectivo])
def crear_evento(request):
    """
    Crea un nuevo evento.
    """
    try:
        data = request.data.copy()
        data['junta_vecinos'] = request.user.junta_vecinos.id
        data['creada_por'] = request.user.id

        serializer = ActividadSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            evento = serializer.save()
            return Response({
                'message': 'Evento creado exitosamente',
                'evento': ActividadSerializer(evento, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': f'Error al crear evento: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def detalle_evento(request, evento_id):
    """
    Obtiene los detalles de un evento.
    """
    try:
        evento = Actividad.objects.get(
            id=evento_id,
            junta_vecinos=request.user.junta_vecinos
        )
        serializer = ActividadSerializer(evento, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Actividad.DoesNotExist:
        return Response({'error': 'Evento no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error al obtener evento: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([EsDirectivo])
def editar_evento(request, evento_id):
    """
    Edita un evento existente.
    """
    try:
        evento = Actividad.objects.get(
            id=evento_id,
            junta_vecinos=request.user.junta_vecinos
        )
        serializer = ActividadSerializer(
            evento,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            evento = serializer.save()
            return Response({
                'message': 'Evento actualizado exitosamente',
                'evento': ActividadSerializer(evento, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Actividad.DoesNotExist:
        return Response({'error': 'Evento no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error al editar evento: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([EsDirectivo])
def eliminar_evento(request, evento_id):
    """
    Elimina un evento.
    """
    try:
        evento = Actividad.objects.get(
            id=evento_id,
            junta_vecinos=request.user.junta_vecinos
        )
        evento.delete()
        return Response({'message': 'Evento eliminado exitosamente'},
                        status=status.HTTP_200_OK)

    except Actividad.DoesNotExist:
        return Response({'error': 'Evento no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error al eliminar evento: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def obtener_inscritos_evento(request, evento_id):
    """
    Obtiene la lista de inscritos de un evento.
    """
    try:
        evento = Actividad.objects.get(
            id=evento_id,
            junta_vecinos=request.user.junta_vecinos
        )
        inscripciones = evento.inscripciones.select_related('vecino').all()

        inscritos_data = []
        for inscripcion in inscripciones:
            inscritos_data.append({
                'id': inscripcion.id,
                'vecino_id': inscripcion.vecino.id,
                'nombre_completo': inscripcion.vecino.get_full_name(),
                'email': inscripcion.vecino.email,
                'rut': inscripcion.vecino.rut,
                'telefono': inscripcion.vecino.telefono,
                'cantidad_acompanantes': inscripcion.cantidad_acompanantes,
                'nombres_acompanantes': inscripcion.nombres_acompanantes,
                'fecha_inscripcion': inscripcion.fecha_inscripcion,
                'total_personas': inscripcion.total_personas
            })

        total_inscritos = inscripciones.count()
        total_personas = sum(i.total_personas for i in inscripciones)

        return Response({
            'evento': {
                'id': evento.id,
                'titulo': evento.titulo,
                'fecha': evento.fecha,
                'cupo_maximo': evento.cupo_maximo,
                'cupo_por_vecino': evento.cupo_por_vecino,
                'permite_acompanantes': evento.permite_acompanantes
            },
            'inscritos': inscritos_data,
            'estadisticas': {
                'total_inscritos': total_inscritos,
                'total_personas': total_personas,
                'cupos_utilizados': total_personas,
                'cupos_disponibles': evento.cupos_disponibles
            }
        }, status=status.HTTP_200_OK)

    except Actividad.DoesNotExist:
        return Response({'error': 'Evento no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error al obtener inscritos: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def exportar_inscritos_evento(request, evento_id):
    """
    Exporta la lista de inscritos a CSV.
    """
    try:
        evento = Actividad.objects.get(
            id=evento_id,
            junta_vecinos=request.user.junta_vecinos
        )
        inscripciones = evento.inscripciones.select_related('vecino').all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="inscritos_{evento.titulo}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            'Nombre', 'Email', 'RUT', 'Teléfono',
            'Acompañantes', 'Nombres Acompañantes',
            'Fecha Inscripción', 'Total Personas'
        ])

        for inscripcion in inscripciones:
            nombres_acompanantes = (
                ', '.join(inscripcion.nombres_acompanantes)
                if isinstance(inscripcion.nombres_acompanantes, list)
                else inscripcion.nombres_acompanantes
            )
            writer.writerow([
                inscripcion.vecino.get_full_name(),
                inscripcion.vecino.email,
                inscripcion.vecino.rut,
                inscripcion.vecino.telefono,
                inscripcion.cantidad_acompanantes,
                nombres_acompanantes,
                inscripcion.fecha_inscripcion.strftime('%Y-%m-%d %H:%M'),
                1 + inscripcion.cantidad_acompanantes
            ])

        return response

    except Actividad.DoesNotExist:
        return Response({'error': 'Evento no encontrado'},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Error al exportar inscritos: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def estadisticas_eventos(request):
    """
    Obtiene estadísticas generales de eventos de la junta de vecinos.
    """
    try:
        ahora = timezone.now()
        eventos = Actividad.objects.filter(junta_vecinos=request.user.junta_vecinos)

        total_eventos = eventos.count()
        eventos_proximos = eventos.filter(fecha__gt=ahora).count()
        eventos_pasados = eventos.filter(fecha__lt=ahora).count()
        eventos_hoy = eventos.filter(fecha__date=ahora.date()).count()

        seis_meses_atras = ahora - timedelta(days=180)
        eventos_por_mes = eventos.filter(
            fecha__gte=seis_meses_atras
        ).annotate(
            mes=TruncMonth('fecha')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')

        return Response({
            'estadisticas_generales': {
                'total_eventos': total_eventos,
                'eventos_proximos': eventos_proximos,
                'eventos_pasados': eventos_pasados,
                'eventos_hoy': eventos_hoy
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error al obtener estadísticas: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([EsVecinoOdirector])
def actualizar_perfil(request):
    """API para actualizar el perfil del vecino"""
    try:
        # Verificar que el usuario sea un vecino o registrado
        user = request.user
        
        # Permitir a vecinos y registrados editar su perfil
        if user.rol not in ['vecino', 'registrado', 'directivo', 'administrador']:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para realizar esta acción'
            }, status=403)
        
        # Leer los datos del request
        data = json.loads(request.body)
        
        # Actualizar el CustomUser
        campos_actualizados = []
        
        if 'first_name' in data and data['first_name']:
            user.nombre = data['first_name']
            campos_actualizados.append('nombre')
        
        if 'last_name' in data and data['last_name']:
            user.apellido = data['last_name']
            campos_actualizados.append('apellido')
        
        if 'email' in data and data['email']:
            # Verificar que el email no esté en uso por otro usuario
            if CustomUser.objects.filter(email=data['email']).exclude(pk=user.pk).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Este correo electrónico ya está en uso'
                }, status=400)
            user.email = data['email']
            campos_actualizados.append('email')
        
        if 'telefono' in data:
            user.telefono = data['telefono']
            campos_actualizados.append('telefono')
        
        if 'direccion' in data:
            user.direccion = data['direccion']
            campos_actualizados.append('direccion')
        
        if campos_actualizados:
            user.save()
        
        # Preparar respuesta
        response_data = {
            'success': True,
            'message': 'Perfil actualizado correctamente',
            'usuario': {
                'id': user.id,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'email': user.email,
                'telefono': user.telefono,
                'direccion': user.direccion,
                'nombre_completo': user.get_full_name(),
                'rol': user.rol,
                'fecha_registro': user.date_joined.isoformat(),
            }
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar el perfil: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def cambiar_password(request):
    try:
        user = request.user
        
        # Leer los datos del request
        data = json.loads(request.body)
        
        # Validar campos requeridos
        required_fields = ['old_password', 'new_password1', 'new_password2']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }, status=400)
        
        # Verificar que las nuevas contraseñas coincidan
        if data['new_password1'] != data['new_password2']:
            return JsonResponse({
                'success': False,
                'message': 'Las contraseñas nuevas no coinciden'
            }, status=400)
        
        # Verificar longitud mínima de la contraseña
        if len(data['new_password1']) < 8:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }, status=400)
        
        # Verificar la contraseña actual
        if not user.check_password(data['old_password']):
            return JsonResponse({
                'success': False,
                'message': 'La contraseña actual es incorrecta'
            }, status=400)
        
        # Cambiar la contraseña
        user.set_password(data['new_password1'])
        user.save()
        
        
        return JsonResponse({
            'success': True,
            'message': 'Contraseña cambiada correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cambiar la contraseña: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def obtener_perfil(request):
    """API para obtener los datos completos del perfil"""
    try:
        user = request.user
        
        # Datos del CustomUser
        perfil_data = {
            'id': user.id,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'email': user.email,
            'telefono': user.telefono,
            'direccion': user.direccion,
            'rut': user.rut,
            'nombre_completo': user.get_full_name(),
            'rol': user.rol,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
        }
        
        # Información de la junta de vecinos si existe
        if user.junta_vecinos:
            perfil_data['junta_vecinos'] = {
                'id': user.junta_vecinos.id,
                'nombre': user.junta_vecinos.nombre,
                'direccion': user.junta_vecinos.direccion,
                'comuna': user.junta_vecinos.comuna,
                'region': user.junta_vecinos.region,
            }
        
        return JsonResponse({
            'success': True,
            'perfil': perfil_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener el perfil: {str(e)}'
        }, status=500)


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import secrets
import requests
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import update_session_auth_hash
from .models import CustomUser
from django.core.cache import cache

# Configuración
VERIFICATION_CODE_LENGTH = 6
CODE_EXPIRATION_MINUTES = 5
MAX_ATTEMPTS = 3

@csrf_exempt
@require_http_methods(["POST"])
def send_verification_code(request):
    """Enviar código de verificación via n8n webhook"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'El email es requerido'
            }, status=400)
        
        # Verificar si el usuario existe (pero no revelar esta información)
        try:
            user = CustomUser.objects.get(email=email, is_active=True)
        except CustomUser.DoesNotExist:
            # Por seguridad, siempre devolver éxito aunque el email no exista
            return JsonResponse({
                'success': True,
                'message': 'Si el email existe en nuestro sistema, recibirás un código de verificación'
            })
        
        # Generar código de verificación
        code = ''.join(secrets.choice('0123456789') for _ in range(VERIFICATION_CODE_LENGTH))
        expiration_time = timezone.now() + timedelta(minutes=CODE_EXPIRATION_MINUTES)
        
        # Guardar código en cache con expiración
        cache_key = f"password_reset_{email}"
        cache_data = {
            'code': code,
            'user_id': user.id,
            'expires_at': expiration_time.isoformat(),
            'attempts': 0,
            'verified': False
        }
        cache.set(cache_key, cache_data, CODE_EXPIRATION_MINUTES * 60)
        
        # Enviar email via n8n webhook
        webhook_success = send_email_via_n8n(email, code, user.nombre)
        if webhook_success:
            return JsonResponse({
                'success': True,
                'message': 'Código de verificación enviado correctamente'
            })
        else:
            return JsonResponse({

                'success': False,
                'message': 'Error al enviar el email. Por favor intenta más tarde.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        # Log del error para debugging (en producción usar logging)
        print(f"Error en send_verification_code: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_code(request):
    """Verificar el código de verificación"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        code = data.get('code', '').strip()
        
        if not email or not code:
            return JsonResponse({
                'success': False,
                'message': 'Email y código son requeridos'
            }, status=400)
        
        # Obtener datos del cache
        cache_key = f"password_reset_{email}"
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return JsonResponse({
                'success': False,
                'message': 'Código expirado o no válido. Solicita uno nuevo.'
            }, status=400)
        
        # Verificar expiración
        expires_at = timezone.datetime.fromisoformat(cache_data['expires_at'])
        if timezone.now() > expires_at:
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'message': 'Código expirado. Solicita uno nuevo.'
            }, status=400)
        
        # Verificar intentos
        if cache_data['attempts'] >= MAX_ATTEMPTS:
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'message': 'Demasiados intentos fallidos. Solicita un nuevo código.'
            }, status=400)
        
        # Verificar código
        if cache_data['code'] != code:
            # Incrementar contador de intentos
            cache_data['attempts'] += 1
            cache.set(cache_key, cache_data, CODE_EXPIRATION_MINUTES * 60)
            
            attempts_left = MAX_ATTEMPTS - cache_data['attempts']
            return JsonResponse({
                'success': False,
                'message': f'Código incorrecto. Te quedan {attempts_left} intentos.'
            }, status=400)
        
        # Código correcto - generar token de verificación
        verification_token = secrets.token_urlsafe(32)
        
        # Actualizar cache con token de verificación
        cache_data['verified'] = True
        cache_data['verification_token'] = verification_token
        cache_data['verified_at'] = timezone.now().isoformat()
        
        # Extender expiración para el token de verificación
        cache.set(cache_key, cache_data, 30 * 60)  # 30 minutos para completar el reset
        
        return JsonResponse({
            'success': True,
            'message': 'Código verificado correctamente',
            'token': verification_token
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en verify_code: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def resend_code(request):
    """Reenviar código de verificación"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'El email es requerido'
            }, status=400)
        
        # Verificar si existe un código previo
        cache_key = f"password_reset_{email}"
        cache_data = cache.get(cache_key)
        
        if cache_data and cache_data.get('verified'):
            return JsonResponse({
                'success': False,
                'message': 'Ya has verificado tu código. Puedes continuar con el proceso.'
            }, status=400)
        
        # Eliminar código anterior si existe
        if cache_data:
            cache.delete(cache_key)
        
        # Reutilizar la función de envío inicial
        return send_verification_code(request)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en resend_code: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def reset_password(request):
    """Restablecer la contraseña después de verificación"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        token = data.get('token', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validaciones básicas
        if not all([email, token, new_password, confirm_password]):
            return JsonResponse({
                'success': False,
                'message': 'Todos los campos son requeridos'
            }, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }, status=400)
        
        # Verificar token de verificación
        cache_key = f"password_reset_{email}"
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return JsonResponse({
                'success': False,
                'message': 'Solicitud expirada. Inicia el proceso nuevamente.'
            }, status=400)
        
        if not cache_data.get('verified') or cache_data.get('verification_token') != token:
            return JsonResponse({
                'success': False,
                'message': 'Token de verificación inválido'
            }, status=400)
        
        # Verificar expiración del token
        verified_at = timezone.datetime.fromisoformat(cache_data['verified_at'])
        if timezone.now() > verified_at + timedelta(minutes=30):
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'message': 'Token expirado. Inicia el proceso nuevamente.'
            }, status=400)
        
        # Obtener usuario y cambiar contraseña
        try:
            user = CustomUser.objects.get(id=cache_data['user_id'], is_active=True)
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=400)
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        # Limpiar cache
        cache.delete(cache_key)
        
        # Enviar email de confirmación
        send_confirmation_email_via_n8n(email, user.get_full_name())
        
        return JsonResponse({
            'success': True,
            'message': 'Contraseña restablecida correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en reset_password: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)

# Funciones auxiliares para n8n
def send_email_via_n8n(email, code, user_name):
    """Enviar email de verificación via n8n webhook"""
    try:
        # URL del webhook de n8n - AJUSTA ESTA URL
        n8n_webhook_url = "http://localhost:5678/webhook-test/9d9ef9d0-76df-446c-8b82-f90cbc79f997"
        
        payload = {
            "email": email,
            "code": code,
            "user_name": user_name,
            "type": "password_reset",
            "expiration_minutes": CODE_EXPIRATION_MINUTES
        }
        
        response = requests.post(
            n8n_webhook_url,
            json=payload,
            timeout=10  # 10 segundos timeout
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling n8n webhook: {str(e)}")
        return False

def send_confirmation_email_via_n8n(email, user_name):
    """Enviar email de confirmación de cambio de contraseña"""
    try:
        n8n_webhook_url = "http://localhost:5678/webhook-test/9d9ef9d0-76df-446c-8b82-f90cbc79f997"
        
        payload = {
            "email": email,
            "user_name": user_name,
            "type": "password_changed",
            "timestamp": timezone.now().isoformat()
        }
        
        response = requests.post(
            n8n_webhook_url,
            json=payload,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling n8n confirmation webhook: {str(e)}")
        return False

@api_view(['GET', 'POST'])
@permission_classes([EsDirectivo])
def espacio_list(request):
    """
    Listar espacios o crear nuevo espacio
    """
    try:
        # Obtener la junta de vecinos del usuario
        junta_vecinos = request.user.junta_vecinos
        if not junta_vecinos:
            return Response(
                {'error': 'Usuario no pertenece a ninguna junta de vecinos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'GET':
            # Listar todos los espacios de la junta de vecinos
            espacios = Espacio.objects.filter(junta_vecinos=junta_vecinos)
            serializer = EspacioSerializer(espacios, many=True)
            return Response({'espacios': serializer.data})
        
        elif request.method == 'POST':
            # Crear nuevo espacio
            serializer = EspacioCreateSerializer(data=request.data)
            if serializer.is_valid():
                # Asignar automáticamente la junta de vecinos del usuario
                espacio = serializer.save(junta_vecinos=junta_vecinos)
                return Response(
                    EspacioSerializer(espacio).data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        print(f"Error en espacio_list: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([EsDirectivo])
def espacio_detail(request, pk):
    """
    Obtener, actualizar o eliminar un espacio específico
    """
    try:
        # Obtener la junta de vecinos del usuario
        junta_vecinos = request.user.junta_vecinos
        if not junta_vecinos:
            return Response(
                {'error': 'Usuario no pertenece a ninguna junta de vecinos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener el espacio que pertenece a la junta de vecinos del usuario
        espacio = get_object_or_404(Espacio, pk=pk, junta_vecinos=junta_vecinos)
        
        if request.method == 'GET':
            serializer = EspacioSerializer(espacio)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = EspacioCreateSerializer(espacio, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(EspacioSerializer(espacio).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            # Verificar si hay solicitudes futuras antes de eliminar
            from django.utils import timezone
            from django.db.models import Q
            
            solicitudes_futuras = espacio.solicitudespacio_set.filter(
                Q(fecha_evento__gte=timezone.now().date()) |
                Q(fecha_evento=timezone.now().date(), hora_inicio__gte=timezone.now().time())
            ).exists()
            
            if solicitudes_futuras:
                return Response(
                    {'error': 'No se puede eliminar el espacio porque tiene reservas futuras'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            espacio.delete()
            return Response(
                {'message': 'Espacio eliminado correctamente'}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Vista para directivos con permisos específicos
@api_view(['GET'])
@permission_classes([EsDirectivo])
def gestion_espacios_directivo(request):
    """
    Vista específica para el panel de directivo con estadísticas
    """
    try:
        junta_vecinos = request.user.junta_vecinos
        if not junta_vecinos:
            return Response(
                {'error': 'Usuario no pertenece a ninguna junta de vecinos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar permisos de directivo
        if not (request.user.es_directivo() or request.user.es_administrador() or request.user.puede_gestionar_calendario):
            return Response(
                {'error': 'No tiene permisos para gestionar espacios'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        espacios = Espacio.objects.filter(junta_vecinos=junta_vecinos)
        serializer = EspacioSerializer(espacios, many=True)
        
        # Calcular estadísticas
        total_espacios = espacios.count()
        disponibles = espacios.filter(disponible=True).count()
        no_disponibles = total_espacios - disponibles
        
        # Contar reservas activas (últimos 30 días)
        from datetime import timedelta
        from django.utils import timezone
        from .models import SolicitudEspacio
        
        fecha_limite = timezone.now().date() - timedelta(days=30)
        reservas_activas = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=junta_vecinos,
            fecha_evento__gte=fecha_limite,
            estado='aprobado'
        ).count()
        
        return Response({
            'espacios': serializer.data,
            'estadisticas': {
                'total_espacios': total_espacios,
                'disponibles': disponibles,
                'no_disponibles': no_disponibles,
                'reservas_activas': reservas_activas
            }
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )