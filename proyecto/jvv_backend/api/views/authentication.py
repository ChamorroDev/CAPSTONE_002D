from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import *
from ..serializers import LoginSerializer, RegisterSerializer, UserSerializer, VecinoRegistrationSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """
    Gestiona el inicio de sesión y verifica si el usuario ha sido aprobado.
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        if user.rol == 'registrado':
            return Response(
                {"error": "Tu cuenta está pendiente de aprobación por la administración."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        refresh = RefreshToken.for_user(user)
        user_serializer = UserLoginSerializer(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def registro_publico_vecino(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Registro exitoso. Esperando aprobación del administrador.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def registro_vecino_api(request):
    """
    API para el registro de nuevos vecinos.
    """
    serializer = VecinoRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Registro exitoso. Su cuenta está pendiente de aprobación por el administrador.'
        }, status=status.HTTP_201_CREATED)
    else:
        print("Errores del serializador:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def current_user(request):
    if not request.user.is_authenticated:
        return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def send_verification_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'El email es requerido'
            }, status=400)
        
        try:
            user = CustomUser.objects.get(email=email, is_active=True)
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': True,
                'message': 'Si el email existe en nuestro sistema, recibirás un código de verificación'
            })
        
        code = ''.join(secrets.choice('0123456789') for _ in range(VERIFICATION_CODE_LENGTH))
        expiration_time = timezone.now() + timedelta(minutes=CODE_EXPIRATION_MINUTES)
        
        cache_key = f"password_reset_{email}"
        cache_data = {
            'code': code,
            'user_id': user.id,
            'expires_at': expiration_time.isoformat(),
            'attempts': 0,
            'verified': False
        }
        cache.set(cache_key, cache_data, CODE_EXPIRATION_MINUTES * 60)
        
        webhook_success = send_email_via_n8n(email, code, user.nombre)
        if webhook_success:
            return JsonResponse({
                'success': True,
                'message': 'Código de verificación enviado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error al enviar el email. Por favor intenta más tarde.'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en send_verification_code: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        code = data.get('code', '').strip()
        
        if not email or not code:
            return JsonResponse({
                'success': False,
                'message': 'Email y código son requeridos'
            }, status=400)
        
        cache_key = f"password_reset_{email}"
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return JsonResponse({
                'success': False,
                'message': 'Código expirado o no válido. Solicita uno nuevo.'
            }, status=400)
        
        expires_at = timezone.datetime.fromisoformat(cache_data['expires_at'])
        if timezone.now() > expires_at:
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'message': 'Código expirado. Solicita uno nuevo.'
            }, status=400)
        
        if cache_data['attempts'] >= MAX_ATTEMPTS:
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'message': 'Demasiados intentos fallidos. Solicita un nuevo código.'
            }, status=400)
        
        if cache_data['code'] != code:
            cache_data['attempts'] += 1
            cache.set(cache_key, cache_data, CODE_EXPIRATION_MINUTES * 60)
            
            attempts_left = MAX_ATTEMPTS - cache_data['attempts']
            return JsonResponse({
                'success': False,
                'message': f'Código incorrecto. Te quedan {attempts_left} intentos.'
            }, status=400)
        
        verification_token = secrets.token_urlsafe(32)
        
        cache_data['verified'] = True
        cache_data['verification_token'] = verification_token
        cache_data['verified_at'] = timezone.now().isoformat()
        
        cache.set(cache_key, cache_data, 30 * 60)  #
        
        return JsonResponse({
            'success': True,
            'message': 'Código verificado correctamente',
            'token': verification_token
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en verify_code: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)


@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def resend_code(request):
    """Reenviar código de verificación"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'El email es requerido'
            }, status=400)
        
        cache_key = f"password_reset_{email}"
        cache_data = cache.get(cache_key)
        
        if cache_data and cache_data.get('verified'):
            return JsonResponse({
                'success': False,
                'message': 'Ya has verificado tu código. Puedes continuar con el proceso.'
            }, status=400)
        
        if cache_data:
            cache.delete(cache_key)
        
        return send_verification_code(request._request)

        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en resend_code: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """Restablecer la contraseña después de verificación"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        token = data.get('token', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([email, token, new_password, confirm_password]):
            return JsonResponse({
                'success': False,
                'message': 'Todos los campos son requeridos'
            }, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres'
            }, status=400)
        cache_key = f"password_reset_{email}"
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return JsonResponse({
                'success': False,
                'message': 'Solicitud expirada. Inicia el proceso nuevamente.'
            }, status=400)
        
        if not cache_data.get('verified') or cache_data.get('verification_token') != token:
            return JsonResponse({
                'success': False,
                'message': 'Token de verificación inválido'
            }, status=400)
        
        verified_at = timezone.datetime.fromisoformat(cache_data['verified_at'])
        if timezone.now() > verified_at + timedelta(minutes=30):
            cache.delete(cache_key)
            return JsonResponse({
                'success': False,
                'message': 'Token expirado. Inicia el proceso nuevamente.'
            }, status=400)
        
        try:
            user = CustomUser.objects.get(id=cache_data['user_id'], is_active=True)
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=400)
        
        user.set_password(new_password)
        user.save()
        
        cache.delete(cache_key)
        
        send_confirmation_email_via_n8n(email, user.get_full_name())
        
        return JsonResponse({
            'success': True,
            'message': 'Contraseña restablecida correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos'
        }, status=400)
    except Exception as e:
        print(f"Error en reset_password: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor'
        }, status=500)
