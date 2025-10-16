import requests
import io
import os
import base64
import json
import re 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .permissions import EsDirectivo
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.utils.timezone import now
import requests
import io
import os
import base64
import json
import re 
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import SolicitudCertificado, JuntaVecinos
from .permissions import EsDirectivo
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.utils.timezone import now

def generar_certificado_pdf_vecino(usuario, motivo_solicitud):

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    junta_vecinos = JuntaVecinos.objects.first()
    junta_de_vecinos_nombre = junta_vecinos.nombre if junta_vecinos else '[Nombre de la Junta]'
    junta_de_vecinos_comuna = junta_vecinos.comuna if junta_vecinos else '[Nombre de la Comuna]'
    junta_de_vecinos_ciudad = junta_vecinos.region if junta_vecinos else '[Nombre de la Ciudad]'

    # Título y encabezado formal
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 2 * cm, "CERTIFICADO DE RESIDENCIA")
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2.0, height - 3 * cm, "(Uso exclusivo para presentación de documentos en la Junta de Vecinos)")
    
    # Contenido del certificado
    p.setFont("Helvetica", 12)
    p.drawString(2 * cm, height - 5 * cm, f"Yo, la Junta de Vecinos de {junta_de_vecinos_nombre}, certifico que:")

    # Datos del residente
    nombre_residente = f"{usuario.nombre} {usuario.apellido}"
    rut_residente = usuario.rut
    direccion_residente = usuario.direccion if hasattr(usuario, 'direccion') and usuario.direccion else 'N/A'
    
    # Declaración de residencia
    p.drawString(2 * cm, height - 6 * cm, f"Don(a) {nombre_residente}, RUT {rut_residente},")
    p.drawString(2 * cm, height - 7 * cm, f"certifica que su domicilio es en {direccion_residente}.")
    p.drawString(2 * cm, height - 8 * cm, f"En la Comuna de {junta_de_vecinos_comuna}, en la Ciudad de {junta_de_vecinos_ciudad}.")
    
    # Párrafo de fe de vida
    p.drawString(2 * cm, height - 9.5 * cm, "Declaro que la información entregada en el presente certificado es fidedigna.")
    p.drawString(2 * cm, height - 10 * cm, "Se extiende este certificado para los fines que estime convenientes, en especial para:")
    p.drawString(2 * cm, height - 10.5 * cm, f"Motivo: {motivo_solicitud}")
    
    # Firma (la parte que causaba el error)
    firma_virtual_path = os.path.join(settings.MEDIA_ROOT, 'firma.png')
    
    try:
        # Verifica si el archivo existe antes de intentar dibujarlo
        if os.path.exists(firma_virtual_path):
            p.drawImage(firma_virtual_path, 2 * cm, 5 * cm, width=4 * cm, height=2 * cm)
        else:
            p.drawString(2 * cm, 5 * cm, "Firma no disponible.")
            print(f"ADVERTENCIA: Archivo de firma no encontrado en: {firma_virtual_path}")
    except Exception as e:
        p.drawString(2 * cm, 5 * cm, "Error al cargar la firma.")
        print(f"Error al cargar la firma: {e}")

    p.setFont("Helvetica", 10)
    p.drawString(2 * cm, 4.5 * cm, "______________________")
    p.drawString(2 * cm, 4 * cm, "Nombre del Presidente/a de la Junta de Vecinos")
    p.drawString(2 * cm, 3.5 * cm, "R.U.T. del Presidente/a")


    p.showPage()
    p.save()

    buffer.seek(0)
    
    return buffer