from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import base64

from .utils import *

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def solicitar_certificado(request):
    serializer = SolicitudCertificadoSerializer(
        data=request.data, 
        context={'request': request}
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
@permission_classes([EsDirectivo])
def lista_certificados_api(request):

    try:
        solicitudes = SolicitudCertificado.objects.all().order_by('-fecha_solicitud')
        
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

@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_certificado(request, certificado_id):

    try:
        solicitud = SolicitudCertificado.objects.get(id=certificado_id)
        
        if solicitud.estado != 'pendiente':
            return Response({'error': 'La solicitud ya ha sido procesada.'}, status=status.HTTP_400_BAD_REQUEST)

        solicitud.estado = 'aprobado'
        solicitud.fecha_resolucion = timezone.now()
        solicitud.resuelto_por = request.user
        solicitud.save()
        
        pdf_buffer = generar_certificado_pdf_vecino(solicitud.vecino, solicitud.motivo)
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        try:
            vecino = solicitud.vecino 
            data_to_send = {
                "nombre_completo": f"{vecino.nombre} {vecino.apellido}",
                "email": vecino.email,
                "rut": vecino.rut,
                "telefono":  re.sub(r'\D', '', vecino.telefono),
                "certificado_base64": pdf_base64
            }

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