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