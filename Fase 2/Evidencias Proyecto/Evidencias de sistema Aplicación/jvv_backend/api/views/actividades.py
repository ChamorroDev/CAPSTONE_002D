from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F, Sum
from .utils import *

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def listar_actividades(request):
    try:
        actividades = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos,
            fecha__gte=timezone.now()
        ).order_by('fecha')
        
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

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def inscribir_actividad(request, actividad_id):
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        
        if actividad.fecha < timezone.now():
            return Response(
                {'error': 'Esta actividad ya ha finalizado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cantidad_acompanantes = request.data.get('cantidad_acompanantes', 0)
        nombres_acompanantes = request.data.get('nombres_acompanantes', [])
        
        try:
            cantidad_acompanantes = int(cantidad_acompanantes)
        except (ValueError, TypeError):
            return Response(
                {'error': 'cantidad_acompanantes debe ser un número válido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cantidad_acompanantes > 0 and len(nombres_acompanantes) != cantidad_acompanantes:
            return Response(
                {'error': f'Debe proporcionar {cantidad_acompanantes} nombres de acompañantes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        puede_inscribirse, mensaje = actividad.puede_inscribirse(request.user, cantidad_acompanantes)
        if not puede_inscribirse:
            return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
        
        inscripcion = InscripcionActividad.objects.create(
            actividad=actividad,
            vecino=request.user,
            cantidad_acompanantes=cantidad_acompanantes,
            nombres_acompanantes=nombres_acompanantes
        )
        
        total_personas = 1 + cantidad_acompanantes
        
        return Response({
            'success': f'Inscripción exitosa para {total_personas} personas',
            'total_personas_inscritas': total_personas
        }, status=status.HTTP_201_CREATED)
        
    except Actividad.DoesNotExist:
        return Response({'error': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        return Response({'error': 'Ya estás inscrito en esta actividad'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Error al inscribirse: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([EsVecinoOdirector])
def cancelar_inscripcion(request, actividad_id):

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

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_inscripciones_detalladas(request):
    try:
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

@api_view(['POST'])
@permission_classes([EsDirectivo])
def crear_evento(request):

    try:
        data = request.data.copy()
        data['junta_vecinos'] = request.user.junta_vecinos.id
        data['creada_por'] = request.user.id

        keys_to_delete = []
        for key, value in data.items():
            if isinstance(value, str) and value == '':
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del data[key]

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
        print(f"Error al crear evento: {str(e)}")
        return Response({'error': f'Error al crear evento: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([EsDirectivo])
def detalle_evento_directivo(request, evento_id):

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


@api_view(['PUT'])
@permission_classes([EsDirectivo])
def editar_evento(request, evento_id):

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

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def lista_eventos_vecino(request):
    try:
        ahora = timezone.now()
        
        actividades = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos,
            fecha__gte=ahora  
        ).order_by('fecha')  
        
        actividades_data = []
        for actividad in actividades:
            esta_inscrito = InscripcionActividad.objects.filter(
                actividad=actividad,
                vecino=request.user
            ).exists()
            
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

@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def mis_inscripciones(request):

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

@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def inscribir_evento(request, evento_id):

    try:
        actividad = Actividad.objects.get(id=evento_id, junta_vecinos=request.user.junta_vecinos)
        
        cantidad_acompanantes = request.data.get('cantidad_acompanantes', 0)
        nombres_acompanantes = request.data.get('nombres_acompanantes', [])
        
        total_personas = 1 + cantidad_acompanantes
        
        puede_inscribirse, mensaje = actividad.puede_inscribirse(request.user, cantidad_acompanantes)
        if not puede_inscribirse:
            return Response(
                {'error': mensaje},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cantidad_acompanantes > 0 and len(nombres_acompanantes) != cantidad_acompanantes:
            return Response(
                {'error': 'La cantidad de nombres de acompañantes no coincide con la cantidad especificada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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



@api_view(['GET'])
@permission_classes([EsDirectivo])
def lista_eventos_directivo(request):

    try:
        eventos = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos
        ).order_by('-fecha')

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

        ahora = timezone.now()
        total_eventos = eventos.count()
        proximos_eventos = eventos.filter(fecha__gt=ahora).count()
        eventos_hoy = eventos.filter(fecha__date=ahora.date()).count()

        total_inscritos_db = Actividad.objects.filter(
            junta_vecinos=request.user.junta_vecinos,  
            fecha__gt=ahora  
        ).aggregate(
            total=Sum(F('inscripciones__cantidad_acompanantes') + 1)
        )

        total_personas_inscritas = total_inscritos_db.get('total') or 0

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
        print(f"Error al obtener eventos: {str(e)}")
        return Response({'error': f'Error al obtener eventos: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)