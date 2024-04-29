from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from usuarios.models import Solicitante

def user_passes_test_httpresponse(test_func):
    """
    Decorador personalizado similar a user_passes_test, pero devuelve un código de respuesta HTTPS en lugar de redireccionar.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Acceso prohibido")  # O cualquier otro código de respuesta HTTPS que desees
        return _wrapped_view
    return decorator


def usuarioEsAdmin(usuario):    
    if usuario.has_perm('permiso_administrador') and usuario.is_superuser == 1:    
        ##print('verificando si usuario es admin True')
        return True
    else:
        ##print('verificando si usuario es admin False')
        return False
    
def usuarioEsSolicitante(usuario):    
    if Solicitante.objects.filter(id=usuario.id).exists() and (not usuario.has_perm('permiso_administrador')):
        #print('verificando si usuario es solicitante True')
        if Solicitante.objects.get(pk=usuario.id).info_completada :  
            #print('verificando si usuario es tiene su info True')
            return True
        else:
            #print('verificando si usuario es tiene su info False')
            return False
    else:
        #print('verificando si usuario es solicitante False')
        return False
    
def usuarioesComun(usuario):
    if usuario.is_authenticated:
        return True
    else:
        return False