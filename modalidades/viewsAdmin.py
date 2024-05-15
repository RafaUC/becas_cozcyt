from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.forms.models import modelformset_factory  #model form for querysets
from django.forms import inlineformset_factory
from usuarios.decorators import user_passes_test, user_passes_test_httpresponse, usuarioEsAdmin
from usuarios.models import Usuario
from django.http import HttpResponse  
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from .forms import *
from .models import *
from .utils import *

# Create your views here.
@login_required
@user_passes_test(usuarioEsAdmin)
def configGeneral(request):
    obj = Convocatoria.get_object() #Obtiene la primera convocatoria ya que solo existirá una
    ciclo = ciclo_actual()
    convocatoriaForm = ConvocatoriaForm()
    cicloForm = CicloForm(instance = ciclo)

    convocatoria_existe = False
    if Convocatoria.objects.exists():
        convocatoria_existe = True
    # print(convocatoria_existe)
    # print(obj.ultimo_ciclo_publicado)
    
    if convocatoria_existe == True: #Si ya existe una convocatoria, los datos se mostrarán deshabilitados y se podrán editar si se requiere
        convocatoriaForm = ConvocatoriaForm(instance = obj)
        context = {'convocatoria' : convocatoriaForm}
        for field in convocatoriaForm.fields.values():
            field.widget.attrs['disabled'] = 'disabled'
        for field in cicloForm.fields.values():
            field.widget.attrs['disabled'] = 'disabled'
        if request.method == "POST":
            convocatoriaForm = ConvocatoriaForm(request.POST or None, request.FILES or None, instance = obj)
            cicloForm = CicloForm(request.POST, instance=ciclo)
            # Eliminar documento en caso de que se suba otro
            # nuevoArchivo = ConvocatoriaForm.instance.archivo_convocatoria #nuevo archivo de convocatoria
            # if ConvocatoriaForm.instance.id and ConvocatoriaForm.instance.archivo_convocatoria is not None:                                                
            #     oldFile = Convocatoria.objects.get(id=ConvocatoriaForm.instance.id).archivo_convocatoria
            #     if ConvocatoriaForm.instance.file != oldFile:                    
            #         oldFile.delete()  
            if convocatoriaForm.is_valid() and cicloForm.is_valid():                
                convocatoriaForm.save()
                cicloForm.save()
                messages.success(request, "Convocatoria actualizada.")            
                return redirect("modalidades:AConfigGeneral")
            else:
                messages.error(request, convocatoriaForm.errors)
                messages.error(request, cicloForm.errors)
            

    else: #Si no hay ninguna convocatoria, se creará una nueva con los campos habilitados
        if request.method == "POST":
            convocatoriaForm = ConvocatoriaForm(request.POST or None, request.FILES or None)
            cicloForm = CicloForm(request.POST, instance=ciclo)
            if convocatoriaForm.is_valid() and cicloForm.is_valid():
                convocatoriaForm.save()
                cicloForm.save()
                messages.success(request, "Convocatoria agregada con éxito.")                
                return redirect("modalidades:AConfigGeneral")
            else:
                messages.error(request, convocatoriaForm.errors)
                messages.error(request, cicloForm.errors)
                print("convocatoria no valida")

    context = {
        'convocatoria':convocatoriaForm, 
        'cicloForm': cicloForm,
        'convocatoria_existe' : convocatoria_existe,
        'ciclo': ciclo,
        }
    return render(request, 'admin/config_general.html', context)


@login_required
@user_passes_test(usuarioEsAdmin)
def togglePublicarUltimosResultados(request):        
    convocatoria = Convocatoria.get_object() #Obtiene la primera convocatoria ya que solo existirá una
    if convocatoria:
        if convocatoria.ultimo_ciclo_publicado and convocatoria.ultimo_ciclo_publicado == ciclo_actual():
            convocatoria.ultimo_ciclo_publicado = None
        else:
            convocatoria.ultimo_ciclo_publicado = ciclo_actual()
        convocatoria.save()

    return redirect('modalidades:AConfigGeneral')


@never_cache
@login_required
@user_passes_test(usuarioEsAdmin)
def configModalidades(request): #se muestran las modalidades        
    modalidades = Modalidad.objects.filter(archivado = False)
    return render(request, 'admin/config_modalidad.html', {'modalidades':modalidades})

# Función que permite mostrar u ocultar una modalidad 
@login_required
@user_passes_test(usuarioEsAdmin)
def mostrar_modalidad(request, modalidad_id):    
    # messages.success(request, "Modalidad actualizada.")
    if request.method == "POST":
        modalidad = Modalidad.objects.get(pk = modalidad_id)
        # print(modalidad)
        seleccion_exitosa = False

        # Muestra u oculta la modalidad
        if (request.POST.get("mostrar", None) == "mostrar_modalidad"):
            if request.POST.get("set_value", None) is not None:
                # print(modalidad, "mostrar")
                modalidad.mostrar = True
                modalidad.save()
                seleccion_exitosa = True
                return HttpResponse((
                    '<div class="jq-toast-single jq-has-icon jq-icon-success" role="alert" style="color: rgb(103, 103, 103); text-align: left;" id="hideMe">'
                    "Modalidad <strong>", modalidad.nombre ,"</strong> se mostrará en convocatoria."
                    "</div>"
                ), status=200, content_type="text/html",)
            elif request.POST.get("set_value", None) is None:
                # print(modalidad,"ocultar")
                modalidad.mostrar = False
                modalidad.save()
                seleccion_exitosa = True
                return HttpResponse(( ""
                    '<div class="jq-toast-single jq-has-icon jq-icon-success" role="alert" style="color: rgb(103, 103, 103); text-align: left;" id="hideMe">'
                    "Modalidad <strong>", modalidad.nombre ,"</strong> no se mostrará en convocatoria."
                    "</div>"
                ), status=200, content_type="text/html",)
            # Si solo se desea mostrar una notificación y no dos, eliminar los dos httpresponse y descomentar el siguiente
            # if seleccion_exitosa:
            #     return HttpResponse((
            #         '<div class="jq-toast-single jq-has-icon jq-icon-success" role="alert" style="color: rgb(103, 103, 103); text-align: left; ">'
            #         "Modalidad <strong>", modalidad.nombre ,"</strong> actualizada."
            #         "</div>"
            #     ), status=200, content_type="text/html",)

@login_required
@user_passes_test(usuarioEsAdmin)
def agregarModalidad(request):      
    modalidad = Modalidad()
    montoModalidad = MontoModalidad(modalidad=modalidad, ciclo = ciclo_actual())
    form = ModalidadForm(request.POST or None, request.FILES or None, instance=modalidad)
    montoForm = MontoModalidadForm(request.POST or None, instance=montoModalidad)
    DocumetoModalidadFormSet = inlineformset_factory(Modalidad, Documento, form=DocumentoForm, extra=0, can_delete=False)
    #Agregar el qs con los documentos base a la variable de qs
    # qs =  Documento.objects.filter(nombre__startswith='C')
    formset = DocumetoModalidadFormSet(request.POST or None, instance=form.instance, prefix='form')
    #print(formset)
    #print(formset.empty_form)
    if request.method == "POST":
        #form = ModalidadForm(request.POST, request.FILES)
        if form.is_valid() and montoForm.is_valid() and formset.is_valid():            
            form.save()
            montoForm.save()
            formset.save()
            # print('modalidad creada')
            
            messages.success(request, "Modalidad creada con éxito.")
            return redirect("modalidades:AConfigModalidades")
        else:
            messages.warning(request, "Porfavor verifique que todos los datos estén llenos.")
            messages.error(request, form.errors)            
            messages.error(request, montoForm.errors)     
            messages.error(request, formset.errors)      
    context = {
            'form' : form,
            'montoForm' : montoForm,
            'formset' : formset
    }
    return render(request, 'admin/config_agregar_modalidad.html', context)

@login_required
@user_passes_test(usuarioEsAdmin)
def editarModalidad(request, modalidad_id):    
    obj = get_object_or_404(Modalidad, pk = modalidad_id)
    imgPath = obj.imagen.path
    montoModalidad = get_object_or_404(MontoModalidad, modalidad=obj, ciclo=ciclo_actual())
    form = ModalidadForm(request.POST or None, request.FILES or None, instance=obj)
    montoForm = MontoModalidadForm(request.POST or None, instance=montoModalidad)
    #formset = modelformset_factory(Model, form=ModelForm, extra=0)
    DocumetoModalidadFormSet = inlineformset_factory(Modalidad, Documento, form=DocumentoForm, extra=0, can_delete=False)    
    formset = DocumetoModalidadFormSet(request.POST or None, instance=form.instance, prefix='form')    
    if request.method == "POST":        
        if form.is_valid() and montoForm.is_valid() and formset.is_valid():
            if len(request.FILES) != 0:
                try:
                    os.remove(imgPath) #Elimina la imagen del folder
                except:
                    pass
                obj.imagen = request.FILES['imagen']
            form.save()            
            montoForm.save()  
            formset.save()            
            messages.success(request, "Cambios guardados.")
            return redirect("modalidades:AConfigModalidades")
        else:
            messages.warning(request, "Porfavor verifique que todos los datos estén llenos.")
            messages.error(request, form.errors)      
            messages.error(request, montoForm.errors)        
            messages.error(request, formset.errors)        
    context = {
        'modalidad' : obj , 
        'form' : form, 
        'montoForm': montoForm,
        'formset' : formset
    }
    return render(request, 'admin/editar_modalidad.html', context)

@login_required
@user_passes_test(usuarioEsAdmin)
def archivarModalidad(request, modalidad_id):   
    modalidad = Modalidad.objects.get(pk = modalidad_id)    
    modalidad.archivado = True
    modalidad.save()
    messages.success(request, "Modalidad archivada correctamente")
    return redirect("modalidades:AConfigModalidades")

@login_required
@user_passes_test(usuarioEsAdmin)
def eliminarModalidad(request, modalidad_id):    
    modalidad = Modalidad.objects.get(pk = modalidad_id)    
    try:
        os.remove(modalidad.imagen.path) #Elimina la imagen del folder
    except:
        pass
    modalidad.delete()
    messages.success(request, "Modalidad eliminada correctamente")
    return redirect("modalidades:AConfigModalidades")

@login_required
@user_passes_test(usuarioEsAdmin)
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

@login_required
@user_passes_test(usuarioEsAdmin)
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