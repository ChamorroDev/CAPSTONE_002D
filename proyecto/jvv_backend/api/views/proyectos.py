from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from ..permissions import *
from django.shortcuts import get_object_or_404
from datetime import  time
from django.utils import timezone

from .utils import (
    EsDirectivo, 
    _enviar_webhook_a_n8n, 
    N8N_WEBHOOK_URL_PROYECTOVECINAL,
    requests,
    json,
    ProyectoVecinal,
    ProyectoVecinalPostSerializer,
    ProyectoVecinalSerializer
)


@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def postular_proyecto(request):
    data = request.data.copy()
    
    if not request.user.junta_vecinos:
        return Response(
            {'error': 'El usuario debe pertenecer a una junta de vecinos para postular un proyecto.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProyectoVecinalPostSerializer(data=data)
    
    if serializer.is_valid():
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
    if not request.user.junta_vecinos:
        return Response(
            {'error': 'El usuario debe pertenecer a una junta de vecinos para ver sus proyectos.'},
            status=status.HTTP_403_FORBIDDEN
        )

    proyectos = ProyectoVecinal.objects.filter(proponente=request.user).order_by('-fecha_creacion')

    serializer = ProyectoVecinalSerializer(proyectos, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


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
            'estado': proyecto.estado, 
            'fecha_resolucion': proyecto.fecha_revision.strftime('%d-%m-%Y %H:%M') if proyecto.fecha_revision else 'N/A', # Fecha de resolución
            'revisado_por': proyecto.revisado_por.get_full_name() if proyecto.revisado_por else 'N/A', # Quién lo revisó
        } for proyecto in proyectos]

        return Response(data)
    except Exception as e:
        error_info = traceback.format_exc()
        print(f"Error en proyectos_lista_api: {error_info}")
        return JsonResponse({'error': str(e)}, status=500)

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


@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(ProyectoVecinal, pk=proyecto_id)
    proyecto.fecha_revision = timezone.now()
    proyecto.estado = 'aprobado'
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
    proyecto.estado = 'rechazado'
    proyecto.revisado_por = request.user
    
    try:
        proyecto.save()
        _enviar_webhook_a_n8n(proyecto, 'rechazo', request.user)
        return Response({'message': 'Proyecto rechazado y webhook enviado.'})
    except IntegrityError as e:
        return Response({'error': str(e)}, status=500)

N8N_WEBHOOK_URL_AVISOS = 'http://localhost:5678/webhook-test/6a6dc069-8dbe-4c3f-8f88-e5d4a330b4e2'
@api_view(['POST'])
@permission_classes([EsDirectivo])
def enviar_aviso_masivo(request):

    usuarios = CustomUser.objects.filter(rol='vecino', is_active=True)

    emails = [u.email for u in usuarios if u.email]
    telefonos = [u.telefono for u in usuarios if u.telefono]

    emails_str = ','.join(emails)
    telefonos_str = ','.join(telefonos)

    telefonos_str = ['+56948031852'] # Para pruebas, eliminar en producciónn
    titulo = request.data.get('titulo')
    contenido = request.data.get('contenido')
    tipo_aviso = request.data.get('tipo_aviso')

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
        print(f"Enviando webhook a n8n con payload: {payload}")
        requests.post(N8N_WEBHOOK_URL_AVISOS, json=payload, timeout=5)
        return Response({'message': 'Aviso enviado para su distribución.'})
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el webhook de aviso a n8n: {e}")
        return Response({'message': 'Aviso recibido, pero hubo un error al enviar el webhook de distribución.'}, status=500)







