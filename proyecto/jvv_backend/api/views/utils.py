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

