from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'nombre', 'apellido', 'rut', 'rol', 'junta_vecinos', 'is_active')
    list_filter = ('rol', 'junta_vecinos', 'is_active')
    search_fields = ('email', 'nombre', 'apellido', 'rut')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'rut', 'telefono', 'direccion', 'fecha_nacimiento')}),
        
        # Nuevo campo de documento de verificación
        ('Documentos de Verificación', {'fields': ('documento_verificacion',)}),
        
        ('Permisos', {'fields': ('rol', 'is_active', 'junta_vecinos', 'groups', 'user_permissions')}),
        ('Permisos específicos', {'fields': (
            'puede_gestionar_vecinos', 
            'puede_gestionar_certificados',
            'puede_gestionar_proyectos', 
            'puede_gestionar_noticias',
            'puede_gestionar_calendario', 
            'puede_gestionar_actividades'
        )}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'nombre', 'apellido', 'rut', 'junta_vecinos', 'rol'),
        }),
    )

admin.site.register(JuntaVecinos)
admin.site.register(Noticia)
admin.site.register(NoticiaImagen)
admin.site.register(SolicitudCertificado)
admin.site.register(ProyectoVecinal)
admin.site.register(Actividad)
admin.site.register(SolicitudEspacio)
