from rest_framework import permissions

class EsAdministrador(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'rol') and 
                request.user.rol == 'administrador')

class EsDirectivo(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'rol') and 
                request.user.rol == 'directivo')

class EsVecino(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'rol') and 
                request.user.rol == 'vecino')

class EsRegistrado(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'rol') and 
                request.user.rol == 'registrado')

class EsVecinoOdirector(permissions.BasePermission):
    """
    Permite el acceso a usuarios con el rol de 'vecino' o 'directivo'.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'rol') and
                (request.user.rol == 'vecino' or request.user.rol == 'directivo'))

class PuedeGestionarVecinos(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.es_administrador() or request.user.puede_gestionar_vecinos))

class PuedeGestionarCertificados(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.es_administrador() or request.user.puede_gestionar_certificados))

class PuedeGestionarProyectos(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.es_administrador() or request.user.puede_gestionar_proyectos))

class PuedeGestionarNoticias(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.es_administrador() or request.user.puede_gestionar_noticias))

class PuedeGestionarActividades(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.es_administrador() or request.user.puede_gestionar_actividades))