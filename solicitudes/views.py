from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

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
    if url: 
        return redirect(url)
    
    if Solicitud.objects.filter(solicitante=solicitante, modalidad=modalidad_id).exists():
        usuario = get_object_or_404(Usuario, pk=request.user.id) 
        solicitante = usuario.solicitante
        modalidad = Modalidad.objects.get(pk = modalidad_id)
        documentos = Documento.objects.filter(modalidad__id=modalidad_id)
        solicitud = Solicitud.objects.get(solicitante=solicitante, modalidad_id=modalidad)
        print(solicitud)
        documentosResp = RespuestaDocumento.objects.filter(solicitud=solicitud)
        listaDocumentos = zip(documentos, documentosResp) #Mete las dos listas de documentos y documentosRespuesta en una sola lista

        context ={
            'modalidad': modalidad,
            'listaDocumentos': listaDocumentos
        }

        if request.method == 'POST':
            for doc in request.FILES:
                documento = Documento.objects.get(id=doc) 
                documentoRespuesta = RespuestaDocumento.objects.get(documento=doc, solicitud=solicitud)
                files=request.FILES[doc] #Se obtiene el documento que se sube
                documentoRespuesta.file.delete() #Se elimina el documento que va a ser modificado
                documentoRespuesta.file = files #Se agrega el nuevo documento
                documentoRespuesta.save() 
                
            messages.success(request, "Documentos modificados con éxito")
            return redirect("solicitudes:convocatorias")

        return render(request, 'usuario_solicitud/modificar_docs_convocatoria.html', context)
      
    else:      
        usuario = get_object_or_404(Usuario, pk=request.user.id) 
        solicitante = usuario.solicitante
        modalidad = Modalidad.objects.get(pk = modalidad_id)
        documentos = Documento.objects.filter(modalidad__id=modalidad_id)
        
        context ={
            'modalidad': modalidad,
            'documentos': documentos
        }
        
        if request.method == 'POST':
            solicitud = Solicitud.objects.create(
                modalidad=modalidad,
                solicitante = solicitante
            )
            for doc in request.FILES:
                files={'file':request.FILES[doc]}
                documento = Documento.objects.get(id=doc)
                data={
                    'solicitud':solicitud,
                    'documento': documento
                }
                formRespDocs = DocumentoRespForm(data=data,files=files)
                
                if formRespDocs.is_valid():
                    formRespDocs.save()
            messages.success(request, "Solicitud creada con éxito")
            return redirect("solicitudes:convocatorias")
        
        return render(request, 'usuario_solicitud/documentos_convocatoria.html', context)
    

# def documentoRespuesta(request, pk=None):
#     documento = Documento.objects.get(id=pk)
#     print("id_documento:", documento)
#     return redirect('documentos_convocatoria')