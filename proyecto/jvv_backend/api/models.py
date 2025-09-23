from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import FileSystemStorage
import os
from .validators import validate_image_size, validate_image_extension

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('El email debe ser proporcionado'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser debe tener is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)

class JuntaVecinos(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField()
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Campos personales
    nombre = models.CharField(_('nombre'), max_length=30)
    apellido = models.CharField(_('apellido'), max_length=30)
    rut = models.CharField(_('RUT'), max_length=12, unique=True)
    telefono = models.CharField(_('teléfono'), max_length=15)
    direccion = models.TextField(_('dirección'))
    fecha_nacimiento = models.DateField(_('fecha de nacimiento'))
    documento_verificacion = models.FileField(upload_to='documentos_verificacion/', null=True, blank=True)
    es_vecino = models.BooleanField(_('es registrado'), default=True)
    
    # Relación con la junta de vecinos
    junta_vecinos = models.ForeignKey(JuntaVecinos, on_delete=models.CASCADE, null=True, blank=True)
    
    # Roles específicos para junta de vecinos
    ROLES = (
        ('registrado', 'Registrado'),
        ('vecino', 'Vecino'),
        ('directivo', 'Directivo'),
        ('administrador', 'Administrador'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='registrado')
    
    # Permisos específicos
    puede_gestionar_vecinos = models.BooleanField(default=False)
    puede_gestionar_certificados = models.BooleanField(default=False)
    puede_gestionar_proyectos = models.BooleanField(default=False)
    puede_gestionar_noticias = models.BooleanField(default=False)
    puede_gestionar_calendario = models.BooleanField(default=False)
    puede_gestionar_actividades = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'rut']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.email}"
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}".strip()
    
    def es_administrador(self):
        return self.rol == 'administrador'
    
    def es_directivo(self):
        return self.rol == 'directivo'
    
    def es_vecino(self):
        return self.rol == 'vecino'

    def es_registrado(self):
        return self.rol == 'registrado'

class SolicitudCertificado(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )
    
    vecino = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    motivo = models.TextField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    resuelto_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificados_resueltos')
    
    def __str__(self):
        return f"Certificado de {self.tipo} - {self.vecino}"

class ProyectoVecinal(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('revision', 'En revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('completado', 'Completado'),
    )
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    proponente = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    junta_vecinos = models.ForeignKey(JuntaVecinos, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    revisado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_revisados')
    
    def __str__(self):
        return self.titulo

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    junta_vecinos = models.ForeignKey('JuntaVecinos', on_delete=models.CASCADE)
    autor = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    es_publica = models.BooleanField(default=True)
    imagen_principal = models.ImageField(
        upload_to='noticias/principal/', 
        null=True, 
        blank=True,
        help_text="Imagen principal de la noticia"
    )
    
    def __str__(self):
        return self.titulo
    
    def obtener_imagen_principal_url(self):
        if self.imagen_principal:
            return self.imagen_principal.url
        elif self.imagenes.exists():
            return self.imagenes.first().imagen.url
        return None
    
    def cantidad_imagenes(self):
        return self.imagenes.count()

# Configuración para el almacenamiento de imágenes
def noticia_image_path(instance, filename):
    # Guardar en: noticias/noticia_{id}/{filename}
    return os.path.join('noticias', f'noticia_{instance.noticia.id}', filename)

class NoticiaImagen(models.Model):
    noticia = models.ForeignKey('Noticia', related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(
        upload_to=noticia_image_path,
        validators=[validate_image_size, validate_image_extension]
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        return f"Imagen {self.id} - {self.noticia.titulo}"

class Actividad(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    cupo_maximo = models.IntegerField(default=0)  # 0 = sin límite
    cupo_por_vecino = models.IntegerField(default=1)  # Máximo de acompañantes + el vecino
    permite_acompanantes = models.BooleanField(default=False)
    junta_vecinos = models.ForeignKey(JuntaVecinos, on_delete=models.CASCADE)
    creada_por = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.titulo
    
    # En models.py - corrige el método cupos_disponibles
    @property
    def cupos_disponibles(self):
        if self.cupo_maximo == 0:
            return float('inf')  # Sin límite
        
        inscritos_total = 0
        for inscripcion in self.inscripciones.all():
            # SUMAR 1 por el vecino + cantidad de acompañantes
            inscritos_total += 1 + inscripcion.cantidad_acompanantes
        
        return max(0, self.cupo_maximo - inscritos_total)

    # Y en el método puede_inscribirse:
    def puede_inscribirse(self, user, cantidad_acompanantes=0):
        if not self.permite_acompanantes and cantidad_acompanantes > 0:
            return False, "Esta actividad no permite acompañantes"
        
        # Verificar que no exceda el máximo por vecino (vecino + acompañantes)
        if cantidad_acompanantes + 1 > self.cupo_por_vecino:
            return False, f"Máximo {self.cupo_por_vecino} personas por inscripción"
        
        # Verificar cupos disponibles considerando vecino + acompañantes
        if self.cupos_disponibles < (1 + cantidad_acompanantes):
            return False, "No hay cupos disponibles"
        
        if self.inscripciones.filter(vecino=user).exists():
            return False, "Ya estás inscrito en esta actividad"
        
        return True, ""

class InscripcionActividad(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='inscripciones')
    vecino = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    cantidad_acompanantes = models.IntegerField(default=0)
    nombres_acompanantes = models.JSONField(default=list, blank=True)  # Lista de nombres
    
    class Meta:
        unique_together = ['actividad', 'vecino']
    
    def __str__(self):
        return f"{self.vecino} + {self.cantidad_acompanantes} acompañantes en {self.actividad}"
    
    @property
    def total_personas(self):
        return 1 + self.cantidad_acompanantes

class Espacio(models.Model):
    TIPOS_ESPACIO = (
        ('cancha', 'Cancha'),
        ('sala', 'Sala Común'),
        ('plaza', 'Plaza'),
        ('otro', 'Otro Espacio'),
    )
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS_ESPACIO)
    descripcion = models.TextField(blank=True)
    disponible = models.BooleanField(default=True)
    junta_vecinos = models.ForeignKey(JuntaVecinos, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class SolicitudEspacio(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )
    
    espacio = models.ForeignKey(Espacio, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_evento = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    aprobado_por = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_aprobadas')
    
    class Meta:
        unique_together = ['espacio', 'fecha_evento', 'hora_inicio']
    
    def __str__(self):
        return f"Reserva de {self.espacio.nombre} - {self.solicitante}"