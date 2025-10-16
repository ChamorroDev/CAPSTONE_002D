from django.shortcuts import render

# Vistas generales

def index(request):
    return render(request, 'home.html')
def perfil_vecino(request):
    return render(request, 'perfil_vecino.html')   
def contacto(request):
    return render(request, 'contacto.html')
def noticias(request):
    return render(request, 'noticias.html')
def detalle_noticia(request):
    return render(request, 'noticia_detalle.html')
def pagina_detalle_noticia(request, noticia_id):
    return render(request, 'noticia_detalle.html', {'noticia_id': noticia_id})
def registro_vecino(request):
    return render(request, 'login/registro.html')
def login_view(request):
    return render(request, 'login/login.html')
def recuperar_password(request):
    return render(request, 'login/recuperar_pass.html')

# Vistas para vecinos

def eventos(request):
    return render(request, 'vecino/eventos.html')
def cambiar_pw(request):
    return render(request, 'vecino/cambiar_pw.html')
def solicitud_espacios(request):
    return render(request, 'vecino/solicitud_espacios.html')
def solicitud_proyecto(request):
    return render(request, 'vecino/solicitud_proyecto.html')
def mi_barrio(request):
    return render(request, 'vecino/mi_barrio.html')
def mis_certificados(request):
    return render(request, 'vecino/mis_certificados.html')
def solicitud_certificado(request):
    return render(request, 'vecino/solicitud_certificado.html')
def mi_perfil(request):
    return render(request, 'vecino/mi_perfil.html')

# Vistas para directivos

def dashboard_directivo(request):
    return render(request, 'directivo/dashboard.html')
def edicion_espacios(request):
    return render(request, 'directivo/espacios/gestion_espacios.html')
def certificados_list(request):
    return render(request, 'directivo/certificados/lista_certificados.html')
def usuarios_lista(request):
    return render(request, 'directivo/usuarios/lista_usuarios.html')
def editar_usuario(request, pk):
    return render(request, 'directivo/usuarios/editar_usuarios.html')
def proyectos_lista(request):
    return render(request, 'directivo/proyectos/lista.html')
def proyecto_detalle(request, proyecto_id):
    return render(request, 'directivo/proyectos/proyecto_detalle.html')
def enviar_avisos(request):
    return render(request, 'directivo/avisos/avisos.html')
def gestion_noticias(request):
    return render(request, 'directivo/noticias/gestion_noticias.html')
def editar_noticias(request, pk):
    return render(request, 'directivo/noticias/editar.html')
def gestion_espacios(request):
    return render(request, 'directivo/espacios/dashboard_espacios.html')
def gestion_eventos(request):
    return render(request, 'directivo/eventos/gestion_eventos.html')