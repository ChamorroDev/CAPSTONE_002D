import io
import json
import requests
import traceback
import re
import secrets
import csv
from datetime import datetime, time, timedelta
from PIL import Image

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import Case, When, Value, ExpressionWrapper, FloatField, F, Q, Count
from django.db.models.functions import ExtractYear, ExtractMonth, TruncMonth
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from ..models import *
from ..serializers import *
from ..permissions import EsAdministrador, EsDirectivo, EsVecino, PuedeGestionarNoticias, EsVecinoOdirector
from ..certificado import generar_certificado_pdf_vecino

# ----- CONSTANTES -----
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/e1d296c6-c14b-451b-a1d3-2b0793e81c7b"
N8N_WEBHOOK_URL_PROYECTOVECINAL = 'http://localhost:5678/webhook/bb27b5d2-4f46-400b-b01b-f24001de5847'
N8N_WEBHOOK_URL_AVISOS = 'http://localhost:5678/webhook/6a6dc069-8dbe-4c3f-8f88-e5d4a330b4e2'
N8N_WEBHOOK_URL_PASSWORD_RESET = "http://localhost:5678/webhook/9d9ef9d0-76df-446c-8b82-f90cbc79f998"
N8N_WEBHOOK_URL_PASSWORD_CONFIRM = "http://localhost:5678/webhook/9d9ef9d0-76df-446c-8b82-f90cbc79f997"


VERIFICATION_CODE_LENGTH = 6
CODE_EXPIRATION_MINUTES = 5
MAX_ATTEMPTS = 3

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

def _enviar_webhook_a_n8n(proyecto, tipo_accion, user):
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

def send_email_via_n8n(email, code, user_name):
    try:
        payload = {
            "email": email,
            "code": code,
            "user_name": user_name,
            "type": "password_reset",
            "expiration_minutes": CODE_EXPIRATION_MINUTES
        }
        
        response = requests.post(
            N8N_WEBHOOK_URL_PASSWORD_RESET,
            json=payload,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling n8n webhook: {str(e)}")
        return False

def send_confirmation_email_via_n8n(email, user_name):
    try:
        payload = {
            "email": email,
            "user_name": user_name,
            "type": "password_changed",
            "timestamp": timezone.now().isoformat()
        }
        
        response = requests.post(
            N8N_WEBHOOK_URL_PASSWORD_CONFIRM,
            json=payload,
            timeout=10
        )
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling n8n confirmation webhook: {str(e)}")
        return False

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contacto(request):
    """
    API para manejar el envío del formulario de contacto a n8n
    """
    try:
        data = json.loads(request.body)
        
        nombre = data.get('nombre', '').strip()
        correo_electronico = data.get('correo_electronico', '').strip()
        mensaje = data.get('mensaje', '').strip()
        
        if not nombre or not correo_electronico or not mensaje:
            return JsonResponse({
                'success': False,
                'message': 'Todos los campos son obligatorios'
            }, status=400)
        
        if len(nombre) < 2 or len(nombre) > 100:
            return JsonResponse({
                'success': False,
                'message': 'El nombre debe tener entre 2 y 100 caracteres'
            }, status=400)
        
        if len(mensaje) < 10 or len(mensaje) > 1000:
            return JsonResponse({
                'success': False,
                'message': 'El mensaje debe tener entre 10 y 1000 caracteres'
            }, status=400)
        
        payload_n8n = {
            "nombre": nombre,
            "email": correo_electronico,
            "mensaje": mensaje,
            "origen": "formulario_contacto_web",
            "timestamp": timezone.now().isoformat()
        }
        
        url_n8n = getattr(settings, 'N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/a0257c4e-08f5-41b7-888f-7446e06257f7')
        
        headers = {
            'Content-Type': 'application/json',
        }
        
    
        
        response = requests.post(
            url_n8n,
            json=payload_n8n,
            headers=headers,
            timeout=30 
        )
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'Tu mensaje ha sido enviado correctamente. Te contactaremos pronto.'
            })
        else:
            print(f"Error n8n - Status: {response.status_code}, Response: {response.text}")
            
            return JsonResponse({
                'success': False,
                'message': 'Error al procesar tu mensaje. Por favor, intenta nuevamente.'
            }, status=500)
        
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'message': 'Tiempo de espera agotado. Por favor, intenta nuevamente.'
        }, status=408)
        
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'success': False,
            'message': 'Error de conexión. Por favor, verifica tu internet e intenta nuevamente.'
        }, status=503)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
        
    except Exception as e:
        print(f"Error interno en api_contacto: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor. Por favor, intenta más tarde.'
        }, status=500)

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import secrets

# Token seguro para webhook
WEBHOOK_TOKEN = settings.WEBHOOK_TOKEN


@csrf_exempt
def webhook_whatsapp(request):
    """
    SOLO verifica si el número es vecino registrado
    n8n se encarga del resto
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    # 1. VERIFICAR TOKEN
    auth_header = request.headers.get('Authorization')
    expected_token = f"Token {settings.WEBHOOK_TOKEN}"
    
    if auth_header != expected_token:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    # 2. PROCESAR MENSAJE
    try:
        import json
        data = json.loads(request.body)
        telefono = data.get('telefono')
        mensaje = data.get('mensaje')
        timestamp = data.get('timestamp')
        
        print(f"📱 Verificando - Tel: {telefono}, Msg: {mensaje}")
        
        # Validar campos requeridos
        if not telefono or not mensaje:
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)
        
        # 3. SOLO VERIFICAR SI ES VECINO
        try:
            vecino = CustomUser.objects.get(telefono=telefono, is_active=True, rol='vecino')
            
            print(f"✅ Vecino verificado: {vecino.get_full_name()}")
            
            # Guardar mensaje (opcional)
            mensaje_obj = MensajeWhatsApp.objects.create(
                vecino=vecino,
                mensaje=mensaje,
                telefono=telefono,
                timestamp=timestamp,
                procesado=True,
                tipo_consulta='verificado'
            )
            
            return JsonResponse({
                'es_vecino': True,
                'vecino_id': vecino.id,
                'nombre': vecino.get_full_name(),
                'telefono': telefono,
                'mensaje': mensaje,
                'mensaje_id': mensaje_obj.id
            })
            
        except CustomUser.DoesNotExist:
            print("❌ No es vecino registrado")
            
            mensaje_obj = MensajeWhatsApp.objects.create(
                mensaje=mensaje,
                telefono=telefono, 
                timestamp=timestamp,
                procesado=False,
                es_vecino=False,
                tipo_consulta='no_verificado'
            )
            
            return JsonResponse({
                'es_vecino': False,
                'telefono': telefono,
                'mensaje': mensaje,
                'motivo': 'no_registrado',
                'mensaje_id': mensaje_obj.id
            })
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def procesar_solicitud(request):
    """q
    Procesa solicitudes de WhatsApp
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    # Verificar token
    auth_header = request.headers.get('Authorization')
    expected_token = f"Token {settings.WEBHOOK_TOKEN}"
    if auth_header != expected_token:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    try:
        data = json.loads(request.body)
        telefono = data.get('telefono')
        tipo_solicitud = data.get('tipo_solicitud')  # 'certificado', 'espacio', 'proyecto'
        
        # Verificar vecino
        try:
            vecino = CustomUser.objects.get(telefono=telefono, is_active=True, rol='vecino')
            
            if tipo_solicitud == 'certificado':
                return procesar_certificado(vecino, data)
            elif tipo_solicitud == 'espacio':
                return procesar_espacio(vecino, data)
            elif tipo_solicitud == 'proyecto':
                return procesar_proyecto(vecino, data)
            else:
                return JsonResponse({'error': 'Tipo de solicitud inválido'}, status=400)
                
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Vecino no registrado'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def procesar_certificado(vecino, data):
    """Procesar solicitud de certificado"""
    # Verificar si ya tiene certificado pendiente
    certificados_pendientes = SolicitudCertificado.objects.filter(
        vecino=vecino, 
        estado='pendiente'
    )
    
    if certificados_pendientes.exists():
        return JsonResponse({
            'estado': 'rechazado',
            'mensaje': '📄 Ya tienes un certificado de residencia pendiente. Espera que el directivo lo apruebe.',
            'solicitud_id': certificados_pendientes.first().id
        })
    
    # Crear nueva solicitud
    solicitud = SolicitudCertificado.objects.create(
        vecino=vecino,
        tipo='Certificado de Residencia',
        motivo='Solicitud vía WhatsApp',
        estado='pendiente'
    )
    
    return JsonResponse({
        'estado': 'creado',
        'mensaje': '✅ Tu solicitud de certificado de residencia ha sido creada. La solictud está en espera del Directivo.',
        'solicitud_id': solicitud.id
    })

def procesar_espacio(vecino, data):
    """Procesar solicitud de espacio"""
    pass

def procesar_proyecto(vecino, data):
    """Procesar propuesta de proyecto con AI estructurado"""
    
    try:
        ai_data = json.loads(data.get('resumen_ai', '{}'))
        titulo = ai_data.get('titulo', f"Propuesta de {vecino.nombre}")
        descripcion = ai_data.get('descripcion', 'Propuesta recibida vía WhatsApp')
        
        proyecto = ProyectoVecinal.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            proponente=vecino,
            junta_vecinos=vecino.junta_vecinos,
            estado='pendiente'
        )
        
        return JsonResponse({
            'estado': 'creado',
            'mensaje': f'✅ Propuesta "{titulo}" registrada exitosamente.',
            'proyecto_id': proyecto.id
        })
        
    except json.JSONDecodeError:
        proyecto = ProyectoVecinal.objects.create(
            titulo=f"Propuesta de {vecino.nombre}",
            descripcion=data.get('resumen_ai', 'Propuesta recibida vía WhatsApp'),
            proponente=vecino,
            junta_vecinos=vecino.junta_vecinos,
            estado='pendiente'
        )
        
        return JsonResponse({
            'estado': 'creado',
            'mensaje': '✅ Tu propuesta ha sido registrada.',
            'proyecto_id': proyecto.id
        })


@csrf_exempt
def estado_conversacion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        telefono = data.get('telefono')
        accion = data.get('accion')  # 'obtener', 'actualizar', 'limpiar'
        
        if accion == 'obtener':
            try:
                conversacion = ConversacionWhatsApp.objects.get(telefono=telefono)
                return JsonResponse({
                    'tiene_conversacion': True,
                    'estado': conversacion.estado,
                    'datos': conversacion.datos_contexto
                })
            except ConversacionWhatsApp.DoesNotExist:
                return JsonResponse({'tiene_conversacion': False})
                
        elif accion == 'actualizar':
            estado = data.get('estado', 'proyecto')
            ConversacionWhatsApp.objects.update_or_create(
                telefono=telefono,
                defaults={'estado': estado, 'datos_contexto': data.get('datos', {})}
            )
            return JsonResponse({'estado': 'actualizado'})
            
        elif accion == 'limpiar':
            ConversacionWhatsApp.objects.filter(telefono=telefono).delete()
            return JsonResponse({'estado': 'limpiado'})