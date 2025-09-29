from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .utils import *
from ..serializers import *

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def vecino_dashboard_api(request):
    try:
        usuario = request.user
        
        noticias = Noticia.objects.filter(
            junta_vecinos=usuario.junta_vecinos,
            es_publica=True
        ).order_by('-fecha_creacion')[:5]
        
        solicitudes_certificados = SolicitudCertificado.objects.filter(vecino=usuario)
        solicitudes_espacios = SolicitudEspacio.objects.filter(solicitante=usuario)
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
                'certificados_totales': solicitudes_certificados.count(),
                'certificados_pendientes': solicitudes_certificados.filter(estado='pendiente').count(),
                'certificados_aprobados': solicitudes_certificados.filter(estado='aprobado').count(),
                'espacios_totales': solicitudes_espacios.count(),
                'espacios_pendientes': solicitudes_espacios.filter(estado='pendiente').count(),
                'espacios_aprobados': solicitudes_espacios.filter(estado='aprobado').count(),
                'proyectos_totales': proyectos_vecinales.count(),
                'proyectos_pendientes': proyectos_vecinales.filter(estado='pendiente').count(),
                'proyectos_aprobados': proyectos_vecinales.filter(estado='aprobado').count(),
                'proyectos_revision': proyectos_vecinales.filter(estado='revision').count(),
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

@api_view(['GET'])
@permission_classes([EsDirectivo])
def directivo_dashboard_api(request):

    try:
        total_vecinos = CustomUser.objects.filter(is_active=True).count()
        pendientes_aprobacion = CustomUser.objects.filter(rol='registrado').count()
        certificados_pendientes = SolicitudCertificado.objects.filter(estado='pendiente').count()
        eventos_activos = Actividad.objects.filter(fecha__gte=timezone.now()).count()
        proyectos_pendientes = ProyectoVecinal.objects.filter(estado='pendiente').count()

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