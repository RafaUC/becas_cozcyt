from django.shortcuts import get_object_or_404, redirect, render
from usuarios.views import verificarRedirect
from usuarios.models import Usuario

# Create your views here.

def configEstudio(request):

    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    return render(request, 'admin/config_estudioSE.html')