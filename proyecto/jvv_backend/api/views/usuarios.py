from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .utils import *
from ..serializers import *

@api_view(['GET'])
@permission_classes([EsAdministrador])
def usuarios_por_junta(request):
    usuarios = CustomUser.objects.filter(junta_vecinos=request.user.junta_vecinos)
    serializer = UserSerializer(usuarios, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([EsAdministrador])
def aprobar_vecino(request, user_id):
    try:
        vecino = CustomUser.objects.get(id=user_id, rol='vecino', is_active=False)
        vecino.is_active = True
        vecino.junta_vecinos = request.user.junta_vecinos
        vecino.save()
        
        return Response({
            'message': f'Vecino {vecino.email} aprobado exitosamente',
            'vecino': UserSerializer(vecino).data
        })
    except CustomUser.DoesNotExist:
        return Response({'error': 'Vecino no encontrado o ya está aprobado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([EsDirectivo])
def aprobar_usuario(request, user_id):

    try:
        user_to_approve = CustomUser.objects.get(id=user_id, rol='registrado')
        user_to_approve.rol = 'vecino'
        user_to_approve.save()
        return Response({'message': 'Usuario aprobado correctamente.'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Usuario no encontrado o ya aprobado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([EsDirectivo])
def rechazar_usuario(request, user_id):

    try:
        user_to_reject = CustomUser.objects.get(id=user_id, rol='registrado')
        user_to_reject.rol = 'rechazado'
        user_to_reject.save()
        return Response({'message': 'Usuario rechazado correctamente.'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Usuario no encontrado o ya procesado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([EsDirectivo])
def directivo_listar_usuarios(request):
    queryset = CustomUser.objects.all()

    search_query = request.query_params.get('search', None)
    if search_query is not None:
        queryset = queryset.filter(
            Q(nombre__icontains=search_query) | 
            Q(apellido__icontains=search_query) |
            Q(rut__icontains=search_query)
        )

    rol_query = request.query_params.get('rol', None)
    if rol_query is not None:
        queryset = queryset.filter(rol=rol_query)

    serializer = CustomUserSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([EsDirectivo])
def directivo_editar_usuario(request, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DirectivoUserSerializer(user)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = DirectivoUserSerializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)