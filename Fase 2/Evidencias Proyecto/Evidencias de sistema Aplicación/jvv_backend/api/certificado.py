import io
import os
from rest_framework.decorators import api_view, permission_classes

from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.utils.timezone import now
import io
import os
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import  JuntaVecinos
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.utils.timezone import now
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import os


def generar_certificado_pdf_vecino(usuario, motivo_solicitud):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ===============================
    #   LOGO ARRIBA IZQUIERDA
    # ===============================
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.jpg')

    if os.path.exists(logo_path):
        p.drawImage(
            logo_path,
            2 * cm,
            height - 4 * cm,   # <-- correcto
            width=4 * cm,
            height=2 * cm
        )


    # ===============================
    #   TÍTULO CENTRADO (BAJADO)
    # ===============================
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 5.5 * cm, "CERTIFICADO DE RESIDENCIA")

    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 6.5 * cm,
                        "(Uso exclusivo para presentación de documentos en la Junta de Vecinos)")


    # ===============================
    #   TEXTO JUSTIFICADO (SUBIDO)
    # ===============================
    style_justificado = ParagraphStyle(
        name="Justificado",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY
    )

    junta = JuntaVecinos.objects.first()
    nombre_junta = junta.nombre if junta else "[Nombre Junta]"
    comuna = junta.comuna if junta else "[Comuna]"
    ciudad = junta.region if junta else "[Ciudad]"

    residente = f"{usuario.nombre} {usuario.apellido}"
    rut = usuario.rut
    direccion = usuario.direccion if hasattr(usuario, 'direccion') and usuario.direccion else "N/A"

    texto = f"""
    Yo, la Junta de Vecinos de {nombre_junta}, certifico que 
    <b>{residente}</b>, RUT {rut}, reside en
    <b>{direccion}</b> ubicada en la comuna de {comuna}, ciudad de {ciudad}. 
    Este certificado se otorga para los fines que el interesado estime conveniente.
    """

    parrafo = Paragraph(texto, style_justificado)

    frame = Frame(
        2 * cm,
        height - 15 * cm,   # <-- SUBIDO (antes -15 cm)
        width - 4 * cm,
        6 * cm,              # <-- altura más pequeña
        showBoundary=0
    )

    frame.addFromList([parrafo], p)


    # ===============================
    #   FIRMA CENTRADA (SUBIDA)
    # ===============================
    firma_path = os.path.join(settings.MEDIA_ROOT, 'firma.png')

    if os.path.exists(firma_path):
        firma_width = 4 * cm
        firma_height = 2 * cm
        firma_x = (width - firma_width) / 2     # centrado
        firma_y = 3.5 * cm                       # <-- SUBIDO (antes 5 cm)

        p.drawImage(
            firma_path,
            firma_x,
            firma_y,
            width=firma_width,
            height=firma_height
        )

    # Línea y textos de firma centrados
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, 3 * cm, "___________________________")
    p.drawCentredString(width / 2, 2.5 * cm, "Presidente/a Junta de Vecinos")
    p.drawCentredString(width / 2, 2 * cm, "R.U.T Presidente/a")

    # Finalizar
    p.showPage()
    p.save()
    buffer.seek(0)

    return buffer