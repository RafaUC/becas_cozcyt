from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage

from .forms import *
from .models import *
from usuarios.models import Usuario
from usuarios.views import verificarRedirect
from modalidades.models import *
from modalidades.forms import *

# Create your views here.
#########################################
# Nota: Recordar
#no cache a las subidas al servidor
##########################################



@never_cache
@login_required
def verificarPdf(request, soli, file):
    documentoRespuesta = get_object_or_404(RespuestaDocumento,pk = file)
    solicitud = get_object_or_404(Solicitud, pk = soli)    
    if(documentoRespuesta.solicitud == solicitud):
        raise Http404("El recurso no existe")
    response = FileResponse(documentoRespuesta.pdf)
    return response


def convocatorias(request):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    modalidades = Modalidad.objects.all()
    return render(request, 'usuario_solicitud/convocatorias.html', {'modalidades':modalidades})



def documentos_convocatorias(request, modalidad_id):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenado su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    obj = Modalidad.objects.get(pk = modalidad_id)
    form = ModalidadForm(request.POST or None, request.FILES or None, instance=obj)
    documentos = obj.get_documentos_children()
    
    solicitudForm = SolicitudForm()
    documentoForm = DocumentoRespForm()
    solicitudForm = SolicitudForm(request.POST or None)
    # print(Modalidad.objects.get(id=modalidad_id))
    # print(Solicitante.objects.get(id=request.user.id))
    DocumetosRespuestaFormSet = modelformset_factory(RespuestaDocumento, form=DocumentoRespForm, extra=0)
    formset = DocumetosRespuestaFormSet(request.POST or None, queryset = RespuestaDocumento.objects.none())
    if request.method == "POST":
        #Se crea la solicitud 
        solicitudForm.instance.modalidad = Modalidad.objects.get(id=modalidad_id)
        solicitudForm.instance.solicitante = Solicitante.objects.get(id=request.user.id)
        print(solicitudForm.instance.modalidad)
        print(solicitudForm.instance.solicitante)
        if solicitudForm.is_valid():
            solicitud = solicitudForm.save(commit=False)
            solicitud.save()
            #Se procesan los documentos
            documentoForm = DocumentoForm(request.POST, request.FILES)
            documentoForm.instance.solicitud = solicitud
            print(solicitud)
            #Se obtiene el id del doc para poder hacer la instancia
            documentoForm.instance.documento = 442
            print(documentoForm.instance.documento)
            documentoForm.save
            documento_id=442
            return redirect("solicitudes:convocatorias")
        else:
            print("nour")
            print(solicitudForm.errors)
            # return redirect("solicitudes:convocatorias")
    context = {
        'modalidad' : obj , 
        'form' : form, 
        'formset' : documentos,
        'documentoForm' : documentoForm,
        'solicitudForm' : solicitudForm,
    }
    return render(request, 'usuario_solicitud/documentos_convocatoria.html', context)


def documentoRespuesta(request, pk=None):
    documento = Documento.objects.get(id=pk)
    print("id_documento:", documento)
    return redirect('documentos_convocatoria')