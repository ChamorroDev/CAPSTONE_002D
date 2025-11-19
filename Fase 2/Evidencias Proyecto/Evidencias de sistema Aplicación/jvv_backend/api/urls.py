from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import authentication, usuarios, noticias, certificados, espacios, actividades, proyectos, dashboard, perfiles,utils,junta_de_vecinos

# Para vistas basadas en clase
router = DefaultRouter()

urlpatterns = [
    # Authentication
    path('api/auth/login/', authentication.login_api, name='login'),
    path('api/auth/register/', authentication.registro_publico_vecino, name='register'),
    path('api/registro/vecino/', authentication.registro_vecino_api, name='registro_vecino_api'),
    path('api/auth/me/', authentication.current_user, name='current_user'),
    
    # Password reset
    path('api/auth/send-verification-code/', authentication.send_verification_code, name='send_verification_code'),
    path('api/auth/verify-code/', authentication.verify_code, name='verify_code'),
    path('api/auth/resend-code/', authentication.resend_code, name='resend_code'),
    path('api/auth/reset-password/', authentication.reset_password, name='reset_password'),
    
    # Dashboard
    path('api/vecino/dashboard/', dashboard.vecino_dashboard_api, name='vecino_dashboard'),
    path('api/dashboard/admin/', dashboard.admin_dashboard_api, name='admin_dashboard'),
    path('api/directivo/dashboard/', dashboard.directivo_dashboard_api, name='directivo_dashboard'),
    
    # Usuarios
    path('api/usuarios/junta/', usuarios.usuarios_por_junta, name='usuarios_por_junta'),
    path('api/usuarios/aprobar/<int:user_id>/', usuarios.aprobar_vecino, name='aprobar_vecino'),
    path('api/directivo/usuarios/', usuarios.directivo_listar_usuarios, name='directivo_listar_usuarios'),
    path('api/directivo/usuarios/editar/<int:pk>/', usuarios.directivo_editar_usuario, name='directivo_editar_usuario'),
    path('api/usuarios/<int:user_id>/aprobar/', usuarios.aprobar_usuario, name='aprobar_usuario'),
    path('api/usuarios/<int:user_id>/rechazar/', usuarios.rechazar_usuario, name='rechazar_usuario'),
    
    # Noticias publicas
    path('api/noticias/', noticias.NoticiaListCreateView.as_view(), name='noticia-list-create'),
    # Noticias
    path('noticias/', noticias.noticias_publicas_api, name='noticias-list'),
    path('api/noticias/<int:noticia_id>/', noticias.detalle_noticia_api, name='detalle_noticia_api'),
    path('api/directivo/noticias/', noticias.noticia_list_create, name='noticia_list_create'),
    path('api/directivo/noticias/<int:pk>/', noticias.noticia_detail_update_delete, name='noticia_detail'),
    path('api/directivo/noticias_imagenes/', noticias.subir_imagen_noticia, name='subir_imagen_noticia'),
    path('api/directivo/noticias_imagenes/<int:pk>/', noticias.eliminar_imagen_noticia, name='eliminar_imagen_noticia'),
    path('api/directivo/noticias/<int:pk>/set_imagen_principal/', noticias.set_imagen_principal, name='set_imagen_principal'),
        
    #Sracraper noticias
    path('api/directivo/noticias/cargar_desde_vitacura/', noticias.NoticiaCargarAPIView.as_view(), name='cargar_noticias_vitacura'),
    
    # Certificados
    path('api/certificados/solicitar/', certificados.solicitar_certificado, name='solicitar_certificado'),
    path('api/certificados/mis-solicitudes/', certificados.mis_solicitudes_certificados, name='mis_solicitudes_certificados'),
    path('api/directivo/certificados/', certificados.lista_certificados_api, name='lista_certificados_api'),
    path('api/directivo/certificados/<int:certificado_id>/aprobar/', certificados.aprobar_certificado, name='aprobar_certificado'),
    path('api/directivo/certificados/<int:certificado_id>/rechazar/', certificados.rechazar_certificado, name='rechazar_certificado'),
    
    # Espacios
    path('api/espacios/', espacios.listar_espacios, name='listar_espacios'),
    path('api/espacios/solicitar/', espacios.solicitar_espacio, name='solicitar_espacio'),
    path('api/espacios/mis-solicitudes/', espacios.mis_solicitudes_espacio, name='mis_solicitudes_espacio'),
    path('api/espacios/disponibilidad/', espacios.disponibilidad_espacios, name='disponibilidad_espacios'),
    path('api/espacios/mis_reservas/', espacios.mis_reservas, name='mis_reservas'),
    path('api/espacios/detalles_dia/', espacios.detalles_dia, name='detalles_dia'),
    path('api/reservas/', espacios.reservas_lista, name='reservas_lista'),

    # Espacios - Directivo
    path('api/directivo/gestion_espacios/', espacios.espacio_list, name='espacio_list'),
    path('api/directivo/gestion_espacios/<int:pk>/', espacios.espacio_detail, name='espacio_detail'),
    path('api/directivo/espacios/gestion/', espacios.gestion_espacios_directivo, name='gestion_espacios_directivo'),
    path('api/directivo/espacios/todas-reservas/', espacios.todas_reservas, name='todas_reservas'),
    path('api/directivo/espacios/todas-solicitudes/', espacios.todas_solicitudes_espacios, name='todas_solicitudes_espacios'),
    path('api/directivo/espacios/solicitudes/<int:pk>/', espacios.detalle_solicitud_espacio, name='detalle_solicitud_espacio'),
    path('api/directivo/espacios/solicitudes/<int:pk>/aprobar/', espacios.aprobar_solicitud_espacio, name='aprobar_solicitud_espacio'),
    path('api/directivo/espacios/solicitudes/<int:pk>/rechazar/', espacios.rechazar_solicitud_espacio, name='rechazar_solicitud_espacio'),
    path('api/directivo/espacios/estadisticas/', espacios.estadisticas_espacios, name='estadisticas_espacios'),
    path('api/directivo/espacios/', espacios.lista_espacios_directivo, name='lista_espacios_directivo'),
    
    # Eventos
    path('api/eventos/', actividades.lista_eventos_vecino, name='lista-eventos-vecino'),
    path('api/mis-inscripciones/', actividades.mis_inscripciones, name='mis-inscripciones'),
    path('api/eventos/<int:evento_id>/cancelar/', actividades.cancelar_inscripcion, name='cancelar-inscripcion'),
    path('api/eventos/<int:evento_id>/inscribir/', actividades.inscribir_evento, name='inscribir-evento'),


    # Actividades
    path('api/actividades/', actividades.listar_actividades, name='listar_actividades'),
    path('api/actividades/<int:actividad_id>/', actividades.detalle_actividad, name='detalle_actividad'),
    path('api/actividades/<int:actividad_id>/inscribir/', actividades.inscribir_actividad, name='inscribir_actividad'),
    path('api/actividades/<int:actividad_id>/cancelar/', actividades.cancelar_inscripcion, name='cancelar_inscripcion'),
    path('api/actividades/mis-inscripciones/', actividades.mis_inscripciones, name='mis_inscripciones'),
    path('api/actividades/mis-inscripciones-detalladas/', actividades.mis_inscripciones_detalladas, name='mis_inscripciones_detalladas'),
    
    # Actividades - Directivo
    path('api/directivo/eventos/', actividades.lista_eventos_directivo, name='lista_eventos_directivo'),
    path('api/directivo/eventos/crear/', actividades.crear_evento, name='crear_evento'),
    path('api/directivo/eventos/<int:evento_id>/', actividades.detalle_evento_directivo, name='detalle_evento_directivo'),
    path('api/directivo/eventos/<int:evento_id>/editar/', actividades.editar_evento, name='editar_evento'),
    path('api/directivo/eventos/<int:evento_id>/eliminar/', actividades.eliminar_evento, name='eliminar_evento'),
    path('api/directivo/eventos/<int:evento_id>/inscritos/', actividades.obtener_inscritos_evento, name='obtener_inscritos_evento'),
    path('api/directivo/eventos/<int:evento_id>/exportar-inscritos/', actividades.exportar_inscritos_evento, name='exportar_inscritos_evento'),
    path('api/directivo/eventos/estadisticas/', actividades.estadisticas_eventos, name='estadisticas_eventos'),
    
    # Proyectos
    path('api/proyectos/postular/', proyectos.postular_proyecto, name='postular_proyecto'),
    path('api/proyectos/vecino-proyectos/', proyectos.vecino_proyectos, name='vecino_proyectos'),
    
    # Proyectos - Directivo
    path('api/proyectos/', proyectos.proyectos_lista_api, name='proyectos_lista_api'),
    path('api/proyectos/<int:proyecto_id>/', proyectos.proyecto_detalle_api, name='proyecto_detalle_api'),
    path('api/proyectos/<int:proyecto_id>/aprobar/', proyectos.aprobar_proyecto, name='aprobar_proyecto'),
    path('api/proyectos/<int:proyecto_id>/rechazar/', proyectos.rechazar_proyecto, name='rechazar_proyecto'),
    
    # Avisos masivos
    path('api/directivo/enviar_aviso_masivo/', proyectos.enviar_aviso_masivo, name='enviar_aviso_masivo'),
    
    # Perfiles
    path('api/vecino/obtener-perfil/', perfiles.obtener_perfil, name='obtener_perfil'),
    path('api/vecino/actualizar-perfil/', perfiles.actualizar_perfil, name='actualizar_perfil'),
    path('api/vecino/cambiar-password/', perfiles.cambiar_password, name='cambiar_password'),
    
    # Contacto

    path('api/contacto/', utils.contacto, name='contacto'),


    path('api/whatsapp/webhook/', utils.webhook_whatsapp , name='webhook_whatsapp'),
    path('api/whatsapp/procesar_solicitud_chat/', utils.procesar_solicitud , name='procesar_solicitud_chat'),
    path('api/whatsapp/estado_conversacion/', utils.estado_conversacion , name='estado_conversacion'),

    # Presidencias - Directivo
    path('api/directivo/establecer_presidente/', junta_de_vecinos.establecer_presidente, name='establecer_presidente'),
    path('api/directivo/actualizar_firma_presidente/', junta_de_vecinos.actualizar_firma, name='actualizar_firma_presidente'),
    path('api/directivo/obtener_firma_presidente/', junta_de_vecinos.obtener_firma_presidente, name='obtener_firma'),
]