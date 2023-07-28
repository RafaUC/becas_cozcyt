from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from usuarios.views import verificarRedirect
from usuarios.models import Usuario

from .forms import *
from .models import *

# Create your views here.

def configModalidades(request): #se muestran las modalidades
    usuario = get_object_or_404(Usuario, pk=request.user.id) 
    modalidades = Modalidad.objects.all()

    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenado su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/config_modalidad.html', {'modalidades':modalidades})


def agregarModalidad(request):
    form = ModalidadForm()
    if request.method == "POST":
        form = ModalidadForm(request.POST, request.FILES)
        if form.is_valid(): 
            modalidad = form.save(commit=False)
            modalidad.save()
            print('modalidad creada') 
            return redirect("modalidades:AConfigModalidades")
        else:
            print('modalidad no creada')
            # return redirect("/administracion/configuracion/modalidades")
    context = {'form' : form}
    return render(request, 'admin/config_agregar_modalidad.html', context)

def editarModalidad(request, modalidad_id):
    modalidad = Modalidad.objects.get(pk = modalidad_id)
    form = ModalidadForm(request.POST or None, request.FILES or None, instance=modalidad)
    if form.is_valid():
        form.save()
        return redirect("modalidades:AConfigModalidades")
    context = {'modalidad' : modalidad , 'form' : form}
    return render(request, 'admin/editar_modalidad.html', context)

def eliminarModalidad(request, modalidad_id):
    modaliadad = Modalidad.objects.get(pk = modalidad_id)
    modaliadad.delete()
    messages.success(request, "Modalidad eliminada correctamente")
    return redirect("modalidades:AConfigModalidades")