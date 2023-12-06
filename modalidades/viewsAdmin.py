from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms.models import modelformset_factory  #model form for querysets
from usuarios.views import verificarRedirect
from usuarios.models import Usuario
from django.http import HttpResponse  
from django.views.decorators.http import require_POST

from .forms import *
from .models import *
from .utils import *

# Create your views here.
def configGeneral(request):
    obj = Convocatoria.objects.all().first()
    convocatoriaForm = ConvocatoriaForm()

    if obj != None: #Si ya existe una convocatoria, los datos se mostrarán deshabilitados y se podrán editar si se requiere
        convocatoriaForm = ConvocatoriaForm(request.POST or None, instance = obj)
        context = {'convocatoria' : convocatoriaForm}
        for field in convocatoriaForm.fields.values():
            field.widget.attrs['disabled'] = 'disabled'
        if request.method == "POST":
            if convocatoriaForm.is_valid():
                fechaI = convocatoriaForm.cleaned_data['fecha_inicio']
                fechaC = convocatoriaForm.cleaned_data['fecha_cierre']
                presup = convocatoriaForm.cleaned_data['presupuesto']
                convocatoriaForm.save()
            messages.success(request, "Convocatoria actualizada.")
            return redirect("modalidades:AConfigGeneral")


    else: #Si no hay ninguna convocatoria, se creará una nueva con los campos habilitados
        if request.method == "POST":
            convocatoriaForm = ConvocatoriaForm(data = request.POST)
            if convocatoriaForm.is_valid():
                fechaI = convocatoriaForm.cleaned_data['fecha_inicio']
                fechaC = convocatoriaForm.cleaned_data['fecha_cierre']
                presup = convocatoriaForm.cleaned_data['presupuesto']

                convocatoria = Convocatoria.objects.create(
                    fecha_inicio = fechaI,
                    fecha_cierre = fechaC,
                    presupuesto = presup
                )
                convocatoria.save()
                messages.success(request, "Convocatoria agregada con éxito.")
                return redirect("modalidades:AConfigGeneral")
            else:
                print("convocatoria no valida")

    context = {'convocatoria':convocatoriaForm }
    return render(request, 'admin/config_general.html', context)

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
    #Agregar el qs con los documentos base a la variable de qs
    # qs =  Documento.objects.filter(nombre__startswith='C')
    formset = DocumetoModalidadFormSet(request.POST or None, queryset = Documento.objects.none())
    if request.method == "POST":
        form = ModalidadForm(request.POST, request.FILES)
        if form.is_valid():
            if all([formset.is_valid()]):
                modalidad = form.save(commit=False)
                modalidad.save() 
                for form in formset:
                    documento = form.save(commit=False)
                    documento.modalidad = modalidad
                    documento.order = get_max_order(modalidad)
                    # documento.order = 
                    documento.save()
            # print('modalidad creada')
            else:
                messages.warning(request, "Porfavor verifique que todos los datos estén llenos.")
                return redirect("modalidades:AConfigAgregarModalidad")
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
            messages.success(request, "Cambios guardados.")
        else:
            messages.warning(request, "Porfavor verifique que todos los datos estén llenos.")
            return redirect("modalidades:AConfigEditarModalidades", modalidad_id)
        return redirect("modalidades:AConfigModalidades")
    return render(request, 'admin/editar_modalidad.html', context)

def eliminarModalidad(request, modalidad_id):
    modalidad = Modalidad.objects.get(pk = modalidad_id)
    if len(modalidad.imagen) > 0:
        os.remove(modalidad.imagen.path) #Elimina la imagen del folder
    modalidad.delete()
    messages.success(request, "Modalidad eliminada correctamente")
    return redirect("modalidades:AConfigModalidades")

def eliminarDocumento(request, modalidad_id ,documento_id):
    # print('ID documento',documento_id)
    # item_id = int(request.POST['modalidad_id'])
    # order = get_object_or_404(Documento, pk=int(request.POST['documento_id']))
    # order.remove_item(item_id)
    # if order.is_empty():                   # if the last item is deleted
    #     order.untie(request.session)
    #     order.delete()
    # return redirect("modalidades:AConfigModalidades")
    documento = Documento.objects.get(pk = documento_id)
    documento.delete()
    messages.success(request, "Documento eliminado correctamente.")
    return redirect("modalidades:AConfigEditarModalidades", modalidad_id)

def ordenarDocumentos(request):
    documentos_id = request.POST.getlist('ordering')
    modalidad_id = request.POST.get('modalidad_id')
    print(documentos_id)
    modalidad = Modalidad.objects.get(pk = modalidad_id)
    form = ModalidadForm(request.POST or None, request.FILES or None, instance=modalidad)
    # qs = modalidad.get_documentos_children()
    # print(qs)
    documentosQS = []
    for idx, documento_id in enumerate(documentos_id, start = 0):
        # documento = qs[idx]
        documento = Documento.objects.get(pk = documento_id)
        print(documento)
        documento.order = idx + 1
        documento.save()
    DocumetoModalidadFormSet = modelformset_factory(Documento, form=DocumentoForm, extra=0, can_order=True)
    qs = modalidad.get_documentos_children()
    print(qs)
    # formset = DocumetoModalidadFormSet(request.POST or None, queryset = qs)
    formset = Documento.objects.filter(modalidad = modalidad)
    # documentos = Documento.objects.all()
    # print(documentos)
    # documentoFormset = DocumentoForm(queryset=documentos, prefix='documento_formset')
    # return render(request, "partials/form_editarmod.html", {'formset' : documentoFormset})
    context = {'modalidad' : modalidad , 'form' : form, 'formset' : formset}
    return render(request, "partials/form_editarmod.html", context)