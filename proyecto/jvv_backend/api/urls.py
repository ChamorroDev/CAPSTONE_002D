from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path('enviar-correo/', enviar_correo, name='enviar_correo'),
    path('enviar-whatsapp/', enviar_whatsapp, name='enviar_whatsapp'),
    path('certificado/', generar_certificado_pdf, name='generar_certificado_pdf'),
    

    # ... otras URLs
    #curl -X POST http://127.0.0.1:8000/enviar-correo/
    #curl -X POST http://127.0.0.1:8000/enviar-whatsapp/
     # ================= VISTAS PÚBLICAS (HTML) =================
    path('', views.index, name='index'),
    path('eventos/', views.eventos, name='eventos'),
    path('contacto/', views.contacto, name='contacto'),
    path('mi-barrio/', views.mi_barrio, name='mi_barrio'),
    path('login/', views.login_view, name='login'),
    path('api/registro/vecino/', registro_vecino_api, name='registro-vecino-api'),

    path('vecino-dashboard/', views.vecino_dashboard, name='vecino_dashboard'),
    path('directivo-dashboard/', views.directivo_dashboard, name='directivo_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # ================= AUTENTICACIÓN =================
    path('api/auth/login/', views.login_api, name='login_api'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', views.current_user, name='current_user'),
    path('api/auth/register/', views.registro_publico_vecino, name='registro_publico'),
    
    # ================= DASHBOARDS API =================
    path('api/vecino/dashboard/', views.vecino_dashboard_api, name='vecino_dashboard_api'),
    path('api/directivo/dashboard/', views.directivo_dashboard_api, name='directivo_dashboard_api'),
    path('api/admin/dashboard/', views.admin_dashboard_api, name='admin_dashboard_api'),

    path('api/usuarios/<int:user_id>/aprobar/', aprobar_usuario, name='aprobar_usuario'),
    path('api/usuarios/<int:user_id>/rechazar/', rechazar_usuario, name='rechazar_usuario'),

    

    # ================= GESTIÓN DE USUARIOS =================
    path('api/users/', views.usuarios_por_junta, name='usuarios_junta'),
    path('api/users/<int:user_id>/approve/', views.aprobar_vecino, name='aprobar_vecino'),
    

    # ================= NOTICIAS =================

    path('noticias/', noticias_publicas_api, name='noticias-list'),

    path('api/noticias/<int:noticia_id>/', views.detalle_noticia_api, name='detalle_noticia_api'),



    # ================= VECINOS-PROYECTOS =================
    path('api/proyectos/postular/', views.postular_proyecto, name='proyecto_postular'),
    path('api/proyectos/vecino-proyectos/', views.vecino_proyectos, name='vecino-proyectos'),


    # ================= VECINOS-CERTIFICADOS =================
    path('api/certificados/solicitar/', views.solicitar_certificado, name='solicitar_certificado'),
    path('api/certificados/mis-solicitudes/', views.mis_solicitudes_certificados, name='mis_solicitudes_certificados'),

    
    # ================= VECINOS-ESPACIOS =================


    # ================= VECINOS-EVENTOS/ACTIVIDADES =================
    path('api/actividades/', views.listar_actividades, name='listar_actividades'),
    path('api/actividades/<int:actividad_id>/', views.detalle_actividad, name='detalle_actividad'),
    path('api/actividades/<int:actividad_id>/inscribir/', views.inscribir_actividad, name='inscribir_actividad'),
    path('api/actividades/<int:actividad_id>/cancelar/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
    path('api/actividades/mis-inscripciones/', views.mis_inscripciones, name='mis_inscripciones'),
    path('api/actividades/mis-inscripciones-detalladas/', views.mis_inscripciones_detalladas, name='mis_inscripciones_detalladas'),
    
    # ================= VISTA DIRECTIVO - CERTIFICADO ==================================
    path('api/directivo/certificados/', lista_certificados_api, name='lista_certificados_api'), 
    path('api/directivo/certificados/<int:certificado_id>/aprobar/', views.aprobar_certificado, name='aprobar_certificado'),
    path('api/directivo/certificados/<int:certificado_id>/rechazar/', views.rechazar_certificado, name='rechazar_certificado'),

    # ================= VISTA DIRECTIVO - USUARIO ==================================
    path('api/directivo/usuarios/', directivo_listar_usuarios, name='directivo_lista-usuarios'),
    path('api/directivo/usuarios/editar/<int:pk>/', directivo_editar_usuario, name='directivo_editar_usuario'),

    # ================= VISTA DIRECTIVO - PROYECTOS ==================================
    path('api/proyectos/', views.proyectos_lista_api, name='proyectos_lista_api'),
    path('api/proyectos/<int:proyecto_id>/', views.proyecto_detalle_api, name='proyecto_detalle_api'),
    path('api/proyectos/<int:proyecto_id>/aprobar/', views.aprobar_proyecto, name='aprobar_proyecto'),
    path('api/proyectos/<int:proyecto_id>/rechazar/', views.rechazar_proyecto, name='rechazar_proyecto'),
    
    path('api/directivo/enviar_aviso_masivo/', enviar_aviso_masivo, name='enviar_aviso_masivo'),

    # ================= VISTA DIRECTIVO - NOTICIAS ==================================
    path('api/directivo/noticias/', noticia_list_create, name='directivo_noticias_listar_crear'),
    path('api/directivo/noticias/<int:pk>/', noticia_detail_update_delete, name='directivo_noticias_detalle'),


    # Rutas para la gestión de noticias y la galería de imágenes
    path('api/directivo/noticias_imagenes/', subir_imagen_noticia, name='noticia-imagen-create'),
    path('api/directivo/noticias_imagenes/<int:pk>/', eliminar_imagen_noticia, name='noticia-imagen-delete'),

    path('api/directivo/noticias/<int:pk>/set_imagen_principal/', views.set_imagen_principal, name='set_imagen_principal'),

    # Endpoints existentes (ya deberían estar)
    path('api/espacios/', views.lista_espacios, name='lista-espacios'),
    path('api/espacios/solicitar/', views.solicitar_espacio, name='solicitar-espacio'),
    
    # Endpoints NUEVOS que necesitamos crear:
    path('api/espacios/mis_reservas/', views.mis_reservas, name='mis-reservas'),
    path('api/espacios/disponibilidad/', views.disponibilidad_espacios, name='disponibilidad-espacios'),
    path('api/espacios/todas-reservas/', views.todas_reservas, name='todas-reservas'),
    path('api/espacios/', views.listar_espacios, name='listar_espacios'),
    path('api/espacios/solicitar/', views.solicitar_espacio, name='solicitar_espacio'),
    path('api/espacios/mis-solicitudes/', views.mis_solicitudes_espacio, name='mis_solicitudes_espacio'),
    path('api/reservas/', reservas_lista, name='reservas_lista'),
    path('api/espacios/detalles_dia/', views.detalles_dia, name='detalles_dia'),


    path('api/directivo/espacios/todas-solicitudes/', views.todas_solicitudes_espacios, name='todas-solicitudes-espacios'),
    path('api/directivo/espacios/solicitudes/<int:pk>/', views.detalle_solicitud_espacio, name='detalle-solicitud-espacio'),
    path('api/directivo/espacios/solicitudes/<int:pk>/aprobar/', views.aprobar_solicitud_espacio, name='aprobar-solicitud-espacio'),
    path('api/directivo/espacios/solicitudes/<int:pk>/rechazar/', views.rechazar_solicitud_espacio, name='rechazar-solicitud-espacio'),
    path('api/directivo/espacios/estadisticas/', views.estadisticas_espacios, name='estadisticas-espacios'),
    path('api/directivo/espacios/', views.lista_espacios_directivo, name='lista-espacios-directivo'),

    # URLs para vecinos
    path('api/eventos/', views.lista_eventos_vecino, name='lista-eventos-vecino'),
    path('api/eventos/<int:evento_id>/inscribir/', views.inscribir_evento, name='inscribir-evento'),
    path('api/eventos/<int:evento_id>/cancelar/', views.cancelar_inscripcion, name='cancelar-inscripcion'),
    path('api/mis-inscripciones/', views.mis_inscripciones, name='mis-inscripciones'),
    

    # Gestión de eventos para directivos
    path('api/directivo/eventos/', views.lista_eventos_directivo, name='lista-eventos-directivo'),
    path('api/directivo/eventos/crear/', views.crear_evento, name='crear-evento'),
    path('api/directivo/eventos/estadisticas/', views.estadisticas_eventos, name='estadisticas-eventos'),
    path('api/directivo/eventos/<int:evento_id>/', views.detalle_evento, name='detalle-evento'),
    path('api/directivo/eventos/<int:evento_id>/editar/', views.editar_evento, name='editar-evento'),
    path('api/directivo/eventos/<int:evento_id>/eliminar/', views.eliminar_evento, name='eliminar-evento'),
    path('api/directivo/eventos/<int:evento_id>/inscritos/', views.obtener_inscritos_evento, name='obtener-inscritos'),
    path('api/directivo/eventos/<int:evento_id>/exportar-inscritos/', views.exportar_inscritos_evento, name='exportar-inscritos'),



    path('api/vecino/actualizar-perfil/', views.actualizar_perfil, name='actualizar_perfil'),
    path('api/vecino/cambiar-password/', views.cambiar_password, name='cambiar_password_api'),
    path('api/vecino/obtener-perfil/', views.obtener_perfil, name='obtener_perfil'),

    path('api/auth/send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('api/auth/verify-code/', views.verify_code, name='verify_code'),
    path('api/auth/resend-code/', views.resend_code, name='resend_code'),
    path('api/auth/reset-password/', views.reset_password, name='reset_password'),


    # URLs para la gestión de espacios
    path('api/directivo/gestion_espacios/', views.espacio_list, name='espacio-list'),
    path('api/directivo/gestion_espacios/<int:pk>/', views.espacio_detail, name='espacio-detail'),
    
    # Vista específica para el panel de directivo
    path('api/directivo/gestion-espacios/', views.gestion_espacios_directivo, name='gestion-espacios-directivo'),

]

