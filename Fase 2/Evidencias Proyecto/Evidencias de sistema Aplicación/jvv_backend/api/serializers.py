from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'nombre', 'apellido', 'rut', 'email', 'direccion', 'rol', 'is_active']

class UserSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    junta_nombre = serializers.CharField(source='junta_vecinos.nombre', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'nombre', 'apellido', 'nombre_completo', 'rut', 
            'telefono', 'direccion', 'fecha_nacimiento', 'rol', 'is_active',
            'junta_vecinos', 'junta_nombre', 'date_joined', 'last_login',
            'puede_gestionar_vecinos', 'puede_gestionar_certificados',
            'puede_gestionar_proyectos', 'puede_gestionar_noticias',
            'puede_gestionar_calendario', 'puede_gestionar_actividades'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}".strip()

class EspacioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Espacio
        fields = ['id', 'nombre', 'tipo', 'descripcion', 'disponible']

class UserLoginSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    junta_nombre = serializers.CharField(source='junta_vecinos.nombre', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'nombre', 'apellido', 'nombre_completo', 'rut',
            'rol', 'is_active', 'junta_vecinos', 'junta_nombre',
            'puede_gestionar_vecinos', 'puede_gestionar_certificados',
            'puede_gestionar_proyectos', 'puede_gestionar_noticias',
            'puede_gestionar_calendario', 'puede_gestionar_actividades'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}".strip()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'password_confirm', 'nombre', 'apellido', 
            'rut', 'telefono', 'direccion', 'fecha_nacimiento'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create(
            **validated_data,
            is_active=False,  
            rol='vecino'     
        )
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                raise serializers.ValidationError('Usuario inactivo')
            raise serializers.ValidationError('Credenciales inválidas')
        raise serializers.ValidationError('Email y contraseña requeridos')

class JuntaVecinosSerializer(serializers.ModelSerializer):
    class Meta:
        model = JuntaVecinos
        fields = ['id', 'nombre', 'direccion', 'comuna', 'region', 'activa']




class SolicitudCertificadoSerializer(serializers.ModelSerializer):
    vecino_nombre = serializers.CharField(source='vecino.get_full_name', read_only=True)
    resuelto_por_nombre = serializers.CharField(source='resuelto_por.get_full_name', read_only=True)
    
    class Meta:
        model = SolicitudCertificado
        fields = [
            'id', 'vecino', 'vecino_nombre', 'tipo', 'motivo', 
            'fecha_solicitud', 'fecha_resolucion', 'estado',
            'resuelto_por', 'resuelto_por_nombre'
        ]
        read_only_fields = ['vecino', 'fecha_solicitud', 'fecha_resolucion', 'resuelto_por']

class ProyectoVecinalPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProyectoVecinal
        fields = ['titulo', 'descripcion', 'proponente', 'junta_vecinos']
        read_only_fields = ['proponente', 'junta_vecinos']

class ProyectoVecinalSerializer(serializers.ModelSerializer):
    proponente_nombre = serializers.CharField(source='proponente.get_full_name', read_only=True)
    revisado_por_nombre = serializers.CharField(source='revisado_por.get_full_name', read_only=True)
    
    class Meta:
        model = ProyectoVecinal
        fields = [
            'id', 'titulo', 'descripcion', 'proponente', 'proponente_nombre',
            'junta_vecinos', 'fecha_creacion', 'fecha_revision', 'estado',
            'revisado_por', 'revisado_por_nombre'
        ]

class InscripcionActividadSerializer(serializers.ModelSerializer):
    vecino_nombre = serializers.CharField(source='vecino.get_full_name', read_only=True)
    actividad_titulo = serializers.CharField(source='actividad.titulo', read_only=True)
    
    class Meta:
        model = InscripcionActividad
        fields = '__all__'
        read_only_fields = ('fecha_inscripcion', 'vecino')

class ActividadSerializer(serializers.ModelSerializer):
    cupos_disponibles = serializers.IntegerField(read_only=True)
    esta_inscrito = serializers.SerializerMethodField()
    mi_inscripcion = serializers.SerializerMethodField()
    
    class Meta:
        model = Actividad
        fields = '__all__'
    
    def get_esta_inscrito(self, obj):
        user = self.context['request'].user
        return obj.inscripciones.filter(vecino=user).exists()
    
    def get_mi_inscripcion(self, obj):
        user = self.context['request'].user
        inscripcion = obj.inscripciones.filter(vecino=user).first()
        if inscripcion:
            return InscripcionActividadSerializer(inscripcion).data
        return None

class SolicitudCertificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudCertificado
        fields = ['id', 'tipo', 'motivo', 'fecha_solicitud', 'estado']
        read_only_fields = ['id', 'fecha_solicitud', 'estado']
    
    def create(self, validated_data):
        validated_data['vecino'] = self.context['request'].user
        return super().create(validated_data)

class EspacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Espacio
        fields = ['id', 'nombre', 'tipo', 'descripcion', 'disponible']  # ← Quitar capacidad

class SolicitudEspacioSerializer(serializers.ModelSerializer):
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    
    class Meta:
        model = SolicitudEspacio
        fields = ['id', 'espacio', 'espacio_nombre', 'fecha_evento', 'hora_inicio', 'hora_fin', 'motivo', 'estado', 'observaciones', 'fecha_solicitud']
        read_only_fields = ['id', 'estado', 'observaciones', 'fecha_solicitud']
    
    def create(self, validated_data):
        validated_data['solicitante'] = self.context['request'].user
        return super().create(validated_data)
    
from rest_framework import serializers
from .models import Noticia, NoticiaImagen

class NoticiaImagenSerializer(serializers.ModelSerializer):
    # Ajustar para que reciba el ID de la noticia
    noticia = serializers.PrimaryKeyRelatedField(
        queryset=Noticia.objects.all(),
        required=True
    )
    
    class Meta:
        model = NoticiaImagen
        fields = ['id', 'imagen', 'noticia'] # El campo 'descripcion' se ha eliminado.

class NoticiaDetalleSerializer(serializers.ModelSerializer):
    imagenes = NoticiaImagenSerializer(many=True, read_only=True)
    
    junta_vecinos = serializers.StringRelatedField()
    autor = serializers.StringRelatedField()
    
    class Meta:
        model = Noticia
        fields = (
            'id',
            'titulo',
            'contenido',
            'junta_vecinos',
            'autor',
            'fecha_creacion',
            'fecha_actualizacion',
            'es_publica',
            'obtener_imagen_principal_url',
            'imagenes',
            'cantidad_imagenes',
        )
class NoticiaSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.get_full_name', read_only=True)
    imagenes = NoticiaImagenSerializer(many=True, read_only=True)
    imagen_principal_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'contenido', 'autor', 'autor_nombre', 
            'junta_vecinos', 'fecha_creacion', 'fecha_actualizacion',
            'es_publica', 'imagen_principal', 'imagen_principal_url', 'imagenes'
        ]
        read_only_fields = ['autor', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_imagen_principal_url(self, obj):
        if obj.imagen_principal:
            return obj.imagen_principal.url
        return None

class NoticiaListSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField()
    obtener_imagen_principal_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = Noticia
        fields = (
            'id',
            'titulo',
            'fecha_creacion',
            'autor',
            'es_publica',
            'obtener_imagen_principal_url'
        )
class VecinoRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'nombre', 'apellido', 'email', 'password', 'rut', 'telefono', 'direccion', 'fecha_nacimiento', 'documento_verificacion')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        documento_verificacion = validated_data.pop('documento_verificacion', None)

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', ''),
            rut=validated_data.get('rut', ''),
            telefono=validated_data.get('telefono', ''),
            direccion=validated_data.get('direccion', ''),
            fecha_nacimiento=validated_data.get('fecha_nacimiento', None)
        )

        if documento_verificacion:
            user.documento_verificacion = documento_verificacion
            user.save()  

        return user

class DirectivoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'nombre', 'apellido', 'email', 'rut', 'telefono', 
            'direccion', 'fecha_nacimiento', 'is_active', 'rol', 
            'documento_verificacion'
        )
        read_only_fields = ('email', 'rut')



class NoticiaEditSerializer(serializers.ModelSerializer):
    imagenes = NoticiaImagenSerializer(many=True, read_only=True)
    imagen_principal = serializers.PrimaryKeyRelatedField(
        queryset=NoticiaImagen.objects.all(),
        allow_null=True
    )

    class Meta:
        model = Noticia
        fields = ['id', 'titulo', 'contenido', 'fecha_creacion', 'fecha_publicacion', 'es_publica', 'imagen_principal', 'imagenes']

    def update(self, instance, validated_data):
        imagen_principal_data = validated_data.pop('imagen_principal', None)
        instance.imagen_principal = imagen_principal_data
        
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.contenido = validated_data.get('contenido', instance.contenido)
        instance.es_publica = validated_data.get('es_publica', instance.es_publica)
        
        instance.save()
        return instance


