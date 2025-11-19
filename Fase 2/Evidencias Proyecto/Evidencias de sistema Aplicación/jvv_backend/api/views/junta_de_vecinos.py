import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ..permissions import EsDirectivo
from ..models import JuntaVecinos, CustomUser
from rest_framework import status
from ..serializers import ConfiguracionPresidenteSerializer


@api_view(['POST'])
@permission_classes([EsDirectivo])
def establecer_presidente(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user_id = request.data.get("user_id")

    if not user_id:
        return Response(
            {"error": "Debe enviar user_id"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    junta = JuntaVecinos.objects.first()

    if not junta:
        return Response(
            {"error": "No existe una Junta de Vecinos configurada"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    junta.presidente = usuario
    junta.save()

    return Response(
        {"mensaje": f"El usuario {usuario.get_full_name()} ahora es el presidente de la Junta."},
        status=status.HTTP_200_OK
    )




@api_view(['POST'])
@permission_classes([EsDirectivo])
def actualizar_firma(request):
    junta = JuntaVecinos.objects.first()

    if not junta:
        return Response(
            {"error": "No hay una Junta de Vecinos configurada."},
            status=status.HTTP_400_BAD_REQUEST
        )

    firma_file = request.FILES.get("firma")

    if not firma_file:
        return Response(
            {"error": "Debe subir un archivo en el campo 'firma'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Si ya hay una firma, eliminar el archivo anterior
    if junta.firma:
        if os.path.exists(junta.firma.path):
            os.remove(junta.firma.path)

    junta.firma = firma_file
    junta.save()

    return Response(
        {"mensaje": "Firma actualizada correctamente."},
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([EsDirectivo])
def obtener_firma_presidente(request):
    junta = JuntaVecinos.objects.first()
    directivos = CustomUser.objects.filter(rol="directivo")

    data = {
        "junta": junta,
        "presidente_actual": junta.presidente,
        "directivos_disponibles": directivos
    }

    serializer = ConfiguracionPresidenteSerializer(data, context={'request': request})
    return Response(serializer.data, status=200)