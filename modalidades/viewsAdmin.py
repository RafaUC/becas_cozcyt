from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms.models import modelformset_factory  #model form for querysets
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
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    form = ModalidadForm()
    DocumetoModalidadFormSet = modelformset_factory(Documento, form=DocumentoForm, extra=0)
    formset = DocumetoModalidadFormSet(request.POST or None, queryset = Modalidad.objects.none())
    if request.method == "POST":
        form = ModalidadForm(request.POST, request.FILES)
        if form.is_valid():
            modalidad = form.save(commit=False)
            modalidad.save() 
            if all([formset.is_valid()]):
                for form in formset:
                    documento = form.save(commit=False)
                    documento.modalidad = modalidad
                    documento.save()
            print('modalidad creada')
        return redirect("modalidades:AConfigModalidades")
    context = {
            'form' : form,
            'formset' : formset
    }
    return render(request, 'admin/config_agregar_modalidad.html', context)

def editarModalidad(request, modalidad_id):
    usuario =  get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    obj = Modalidad.objects.get(pk = modalidad_id)
    form = ModalidadForm(request.POST or None, request.FILES or None, instance=obj)
    #formset = modelformset_factory(Model, form=ModelForm, extra=0)
    DocumetoModalidadFormSet = modelformset_factory(Documento, form=DocumentoForm, extra=0)
    qs = obj.get_documentos_children()
    formset = DocumetoModalidadFormSet(request.POST or None, queryset = qs)
    context = {
        'modalidad' : obj , 
        'form' : form, 
        'formset' : formset
    }
    if request.method == "POST":
        if len(request.FILES) != 0:
            if len(obj.imagen) > 0: 
                os.remove(obj.imagen.path) #Elimina la imagen del folder
            obj.imagen = request.FILES['imagen']
        if all([form.is_valid(), formset.is_valid()]):
            parent = form.save(commit=False)
            parent.save()
            #formset.save()
            for form in formset:
                child = form.save(commit=False)
                child.modalidad = parent
                child.save()
        return redirect("modalidades:AConfigModalidades")
    return render(request, 'admin/editar_modalidad.html', context)

def eliminarModalidad(request, modalidad_id):
    modalidad = Modalidad.objects.get(pk = modalidad_id)
    if len(modalidad.imagen) > 0:
        os.remove(modalidad.imagen.path) #Elimina la imagen del folder
    modalidad.delete()
    messages.success(request, "Modalidad eliminada correctamente")
    return redirect("modalidades:AConfigModalidades")

def eliminarDocumento(request, documento_id):
    documento = Documento.objects.get(pk = documento_id)
    documento.delete()
    return redirect("modalidades:AConfigEditarModalidades")