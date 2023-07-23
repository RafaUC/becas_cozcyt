from django.shortcuts import get_object_or_404, redirect, render
from usuarios.views import verificarRedirect
from usuarios.models import Usuario

from .forms import *
from .models import *

# Create your views here.

def configModalidades(request):

    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenado su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    return render(request, 'admin/config_modalidad.html')

def agregarModalidad(request):
    form = ModalidadForm()
    if request.method == "POST":
        form = ModalidadForm(data=request.POST)
        if form.is_valid(): 
            print('modalidad creada') 
        else:
            print('modalidad no creada')
    context = {'form' : form}
    return render(request, 'admin/config_agregar_modalidad.html', context)