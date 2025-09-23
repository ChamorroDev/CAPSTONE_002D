from django.contrib import admin
from django.urls import path
from webapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('noticias/', views.noticias, name='noticias'),
    path('eventos/', views.eventos, name='eventos'),
    path('detalle_noticia/', views.detalle_noticia, name='detalle_noticia'),
    path('contacto/', views.contacto, name='contacto'),
    path('registro/', views.registro_vecino, name='registro_vecino'),
    path('login/', views.login_view, name='login'),
    path('vecino-dashboard/', views.mi_barrio, name='mi_barrio'),
    path('mis_certificados/', views.mis_certificados, name='mis_certificados'),
    path('solicitud_certificado/', views.solicitud_certificado, name='solicitud_certificado'),
    path('perfil_vecino/', views.perfil_vecino, name='perfil_vecino'),
    path('cambiar_pw/', views.cambiar_pw, name='cambiar_pw'),
    path('solicitud_espacios/', views.solicitud_espacios, name='solicitud_espacios'),
    path('solicitud_proyecto/', views.solicitud_proyecto, name='solicitud_proyecto'),
    path('noticias/<int:noticia_id>/', views.pagina_detalle_noticia, name='detalle_noticia'),
    path('directivo-dashboard/', views.dashboard_directivo, name='dashboard_directivo'),

    path('certificados-lista/', views.certificados_list, name='certificados_lista'), 
    path('usuarios-lista/', views.usuarios_lista, name='usuarios_lista'), 
    path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),


    path('proyectos_lista/', views.proyectos_lista, name='proyectos_lista'),
    path('enviar_avisos/', views.enviar_avisos, name='enviar_avisos'),
    path('proyectos/<int:proyecto_id>/', views.proyecto_detalle, name='proyecto_detalle'),

    path('gestion_noticias/', views.gestion_noticias, name='gestion_noticias'),
    path('gestion_noticias/editar/<int:pk>/', views.editar_noticias, name='editar_noticias'),

    path('gestion_espacios/', views.gestion_espacios, name='gestion_espacios'),

    path('gestion_eventos/', views.gestion_eventos, name='gestion_eventos'),
    path('mi_perfil/', views.mi_perfil, name='mi_perfil'),
    path('recuperar_password/', views.recuperar_password, name='recuperar_password'),

    path('edicion_espacios/', views.edicion_espacios, name='edicion_espacios'),






    


    



]