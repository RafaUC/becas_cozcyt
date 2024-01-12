from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage
from pathlib import Path
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
def verPDF(request, soli, file):
    documento_respuesta = get_object_or_404(RespuestaDocumento, pk=file)
    solicitud = get_object_or_404(Solicitud, pk=soli)

    # Verificar si el documento pertenece a la solicitud
    if documento_respuesta.solicitud != solicitud:
        raise Http404("El recurso no existe")

    # Construir la ruta completa al archivo PDF
    ruta_path = Path(f'{settings.MEDIA_ROOT}{documento_respuesta.file}') 

    # Verificar si el archivo existe antes de intentar abrirlo
    if not ruta_path.is_file():
        raise Http404("El archivo no existe")

    # Verificar si el archivo es un PDF (opcional)
    if not ruta_path.suffix.lower() == ".pdf":
        raise Http404("El archivo no es un PDF")

    # Abrir el archivo y generar una FileResponse
    with open(ruta_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(ruta_path)}"'
        return response

def convocatorias(request):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    modalidades = Modalidad.objects.all()
    convocatoria = Convocatoria.objects.all().first()
    context = {
        'modalidades' : modalidades,
        'convocatoria' : convocatoria
    }
    return render(request, 'usuario_solicitud/convocatorias.html', context)

def documentos_convocatorias(request, modalidad_id):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url: 
        return redirect(url)
    
    #Si el usuario ya subió su documentación se le muestra la vista para modificar sus documentos
    if Solicitud.objects.filter(solicitante=solicitante, modalidad=modalidad_id, ciclo = ciclo_actual()).exists():
        usuario = get_object_or_404(Usuario, pk=request.user.id) 
        solicitante = usuario.solicitante
        modalidad = Modalidad.objects.get(pk = modalidad_id)
        documentos = Documento.objects.filter(modalidad__id=modalidad_id)
        solicitud = Solicitud.objects.get(solicitante=solicitante, modalidad_id=modalidad, ciclo=ciclo_actual())
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
                print(files)
                documentoRespuesta.file.delete() #Se elimina el documento que va a ser modificado
                documentoRespuesta.file = files #Se agrega el nuevo documento
                documentoRespuesta.save() 
                
            messages.success(request, "Documentos modificados con éxito")
            return redirect("solicitudes:convocatorias")

        return render(request, 'usuario_solicitud/modificar_docs_convocatoria.html', context)
      
    #Si el usuario aún no sube documentación para la modalidad elegida, se le muestra la vista para subir sus documentos
    else:      
        usuario = get_object_or_404(Usuario, pk=request.user.id) 
        solicitante = usuario.solicitante
        modalidad = Modalidad.objects.get(pk = modalidad_id)
        documentos = Documento.objects.filter(modalidad__id=modalidad_id)
        convocatoria = Convocatoria.objects.all().first()
        
        context ={
            'modalidad': modalidad,
            'documentos': documentos,
            'convocatoria' : convocatoria,
        }
        
        if request.method == 'POST':
            
            if Solicitud.objects.filter(solicitante=solicitante, ciclo = ciclo_actual()).exists(): #El solicitante ya tiene una solicitud del ciclo actual
                solicitud = Solicitud.objects.get(solicitante=solicitante, ciclo = ciclo_actual())
                messages.warning(request, f'Ya estás participando en la modalidad de {solicitud.modalidad}')
            
            else: #El solicitante no ha hecho una solicitud en el ciclo actual
                solicitud = Solicitud.objects.create(
                    modalidad=modalidad,
                    solicitante = solicitante
                )
                for doc in request.FILES:
                    files={'file':request.FILES[doc]}
                    documento = Documento.objects.get(id=doc)
                    estado = "pendiente"
                    data={
                        'solicitud':solicitud,
                        'documento': documento,
                        'estado' : estado,
                    }
                    formRespDocs = DocumentoRespForm(data=data,files=files)
                    
                    if formRespDocs.is_valid():
                        formRespDocs.save()
                messages.success(request, "Solicitud creada con éxito")
                return redirect("solicitudes:convocatorias")
        
        return render(request, 'usuario_solicitud/documentos_convocatoria.html', context)
    

def documentoRespuesta(request, pk=None):
    documento = Documento.objects.get(id=pk)
    print("id_documento:", documento)
    return redirect('documentos_convocatoria')

@login_required
def historial(request):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    solicitudes = Solicitud.objects.filter(solicitante = solicitante).order_by('-id')

    context = {
        'solicitudes': solicitudes,
        'solicitante': solicitante
    }

    return render(request, 'solicitante/historial.html', context)
