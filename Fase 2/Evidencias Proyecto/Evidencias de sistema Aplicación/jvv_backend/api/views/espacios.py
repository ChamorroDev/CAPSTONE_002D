from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .utils import *

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
        espacio_id = request.data.get('espacio')
        fecha_evento = request.data.get('fecha_evento')
        hora_inicio = request.data.get('hora_inicio')
        
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

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def disponibilidad_espacios(request):

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
@permission_classes([EsVecinoOdirector])
def mis_reservas(request):
    try:
        reservas = SolicitudEspacio.objects.filter(
            solicitante=request.user
        ).select_related('espacio').order_by('-fecha_solicitud')
        
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
def detalles_dia(request):

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

    reservas_del_dia = SolicitudEspacio.objects.filter(
        espacio_id=espacio_id,
        fecha_evento=fecha,
        estado__in=['aprobado', 'pendiente']
    ).order_by('hora_inicio') 

    serializer = SolicitudEspacioSerializer(reservas_del_dia, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([EsDirectivo])
def espacio_list(request):

    try:
        junta_vecinos = request.user.junta_vecinos
        if not junta_vecinos:
            return Response(
                {'error': 'Usuario no pertenece a ninguna junta de vecinos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'GET':
            espacios = Espacio.objects.filter(junta_vecinos=junta_vecinos)
            serializer = EspacioSerializer(espacios, many=True)
            return Response({'espacios': serializer.data})
        
        elif request.method == 'POST':
            serializer = EspacioCreateSerializer(data=request.data)
            if serializer.is_valid():
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

@api_view(["GET"])
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
        
        if not (request.user.es_directivo() or request.user.es_administrador() or request.user.puede_gestionar_calendario):
            return Response(
                {'error': 'No tiene permisos para gestionar espacios'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        espacios = Espacio.objects.filter(junta_vecinos=junta_vecinos)
        serializer = EspacioSerializer(espacios, many=True)
        
        total_espacios = espacios.count()
        disponibles = espacios.filter(disponible=True).count()
        no_disponibles = total_espacios - disponibles
        

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

@api_view(['GET'])
@permission_classes([EsDirectivo])
def todas_reservas(request):
    """
    Obtiene todas las reservas de la junta de vecinos (para directivos)
    """
    try:
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
@permission_classes([EsDirectivo])
def todas_solicitudes_espacios(request):

    try:
        estado = request.GET.get('estado')
        espacio_id = request.GET.get('espacio')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        solicitudes = SolicitudEspacio.objects.filter(
            espacio__junta_vecinos=request.user.junta_vecinos
        ).select_related('espacio', 'solicitante', 'aprobado_por').order_by('-fecha_solicitud')
        
        if estado:
            solicitudes = solicitudes.filter(estado=estado)
        
        if espacio_id:
            solicitudes = solicitudes.filter(espacio_id=espacio_id)
        
        if fecha_desde:
            solicitudes = solicitudes.filter(fecha_solicitud__date__gte=fecha_desde)
        
        if fecha_hasta:
            solicitudes = solicitudes.filter(fecha_solicitud__date__lte=fecha_hasta)
        
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
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def detalle_solicitud_espacio(request, pk):

    try:
        solicitud = SolicitudEspacio.objects.select_related(
            'espacio', 'solicitante', 'aprobado_por'
        ).get(
            id=pk,
            espacio__junta_vecinos=request.user.junta_vecinos
        )
        
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
        print(f"Intentando aprobar solicitud {pk}") 
        
        solicitud = SolicitudEspacio.objects.get(
            id=pk,
            espacio__junta_vecinos=request.user.junta_vecinos,
            estado='pendiente'  #
        )
        
        print(f"Solicitud encontrada: {solicitud}")  
        
        conflicto = SolicitudEspacio.objects.filter(
            espacio=solicitud.espacio,
            fecha_evento=solicitud.fecha_evento,
            hora_inicio__lt=solicitud.hora_fin,
            hora_fin__gt=solicitud.hora_inicio,
            estado='aprobado'
        ).exclude(id=pk).exists()
        
        if conflicto:
            print("Conflicto de horario detectado")  
            return Response(
                {'error': 'Ya existe una reserva aprobada en ese horario'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = 'aprobado'
        solicitud.aprobado_por = request.user
        solicitud.save()
        
        print("Solicitud aprobada exitosamente")  
        
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

    try:
        solicitud = SolicitudEspacio.objects.get(
            id=pk,
            espacio__junta_vecinos=request.user.junta_vecinos,
            estado='pendiente'  
        )
        
        motivo = request.data.get('motivo')
        if not motivo or not motivo.strip():
            return Response(
                {'error': 'El motivo del rechazo es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        solicitud.estado = 'rechazado'
        solicitud.aprobado_por = request.user
        solicitud.observaciones = f"Rechazado: {motivo.strip()}"
        solicitud.save()
        
        
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
        
        seis_meses_atras = timezone.now() - timezone.timedelta(days=180)
        
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
def reservas_lista(request):
    user = request.user
    if not user.junta_vecinos:
        return Response({'error': 'El usuario no pertenece a una junta de vecinos'}, status=status.HTTP_403_FORBIDDEN)

    reservas = SolicitudEspacio.objects.filter(
        espacio__junta_vecinos=user.junta_vecinos,
        estado__in=['aprobado', 'pendiente']
    ).select_related('espacio', 'solicitante') 

    serializer = SolicitudEspacioSerializer(reservas, many=True)
    return Response(serializer.data)


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
