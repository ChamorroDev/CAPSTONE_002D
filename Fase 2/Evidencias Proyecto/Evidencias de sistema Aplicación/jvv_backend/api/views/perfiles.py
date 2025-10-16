from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import json

from .utils import *

@api_view(['PUT'])
@permission_classes([EsVecinoOdirector])
def actualizar_perfil(request):
    try:
        user = request.user
        
        if user.rol not in ['vecino', 'registrado', 'directivo', 'administrador']:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para realizar esta acción'
            }, status=403)
        
        data = json.loads(request.body)
        campos_actualizados = []
        
        if 'first_name' in data and data['first_name']:
            user.nombre = data['first_name']
            campos_actualizados.append('nombre')
        
        if 'last_name' in data and data['last_name']:
            user.apellido = data['last_name']
            campos_actualizados.append('apellido')
        
        if 'email' in data and data['email']:
            if CustomUser.objects.filter(email=data['email']).exclude(pk=user.pk).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Este correo electrónico ya está en uso'
                }, status=400)
            user.email = data['email']
            campos_actualizados.append('email')
        
        if 'telefono' in data:
            user.telefono = data['telefono']
            campos_actualizados.append('telefono')
        
        if 'direccion' in data:
            user.direccion = data['direccion']
            campos_actualizados.append('direccion')
        
        if campos_actualizados:
            user.save()
        
        response_data = {
            'success': True,
            'message': 'Perfil actualizado correctamente',
            'usuario': {
                'id': user.id,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'email': user.email,
                'telefono': user.telefono,
                'direccion': user.direccion,
                'nombre_completo': user.get_full_name(),
                'rol': user.rol,
                'fecha_registro': user.date_joined.isoformat(),
            }
        }
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar el perfil: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([EsVecinoOdirector])
def obtener_perfil(request):
    try:
        user = request.user
        
        perfil_data = {
            'id': user.id,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'email': user.email,
            'telefono': user.telefono,
            'direccion': user.direccion,
            'rut': user.rut,
            'nombre_completo': user.get_full_name(),
            'rol': user.rol,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
        }
        
        if user.junta_vecinos:
            perfil_data['junta_vecinos'] = {
                'id': user.junta_vecinos.id,
                'nombre': user.junta_vecinos.nombre,
                'direccion': user.junta_vecinos.direccion,
                'comuna': user.junta_vecinos.comuna,
                'region': user.junta_vecinos.region,
            }
        
        return JsonResponse({
            'success': True,
            'perfil': perfil_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener el perfil: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([EsVecinoOdirector])
def cambiar_password(request):
    try:
        user = request.user
        
        data = json.loads(request.body)
        
        required_fields = ['old_password', 'new_password1', 'new_password2']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }, status=400)
        
        if data['new_password1'] != data['new_password2']:
            return JsonResponse({
                'success': False,
                'message': 'Las contraseñas nuevas no coinciden'
            }, status=400)
        
        if len(data['new_password1']) < 8:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }, status=400)
        
        if not user.check_password(data['old_password']):
            return JsonResponse({
                'success': False,
                'message': 'La contraseña actual es incorrecta'
            }, status=400)
        
        user.set_password(data['new_password1'])
        user.save()
        
        
        return JsonResponse({
            'success': True,
            'message': 'Contraseña cambiada correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cambiar la contraseña: {str(e)}'
        }, status=500)

















