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
from django.http import HttpResponseForbidden


from .forms import *
from .models import *
from usuarios.models import Usuario
from usuarios.views import verificarRedirect
from modalidades.models import *
from modalidades.forms import *

from mensajes import notificaciones as notif
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
    if not((request.user.has_perm('permiso_administrador') and request.user.is_superuser == 1) or request.user.id == solicitud.solicitante_id ): 
        return HttpResponseForbidden("No tienes los permisos necesarios para acceder a este documento.")
    

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

@never_cache
@login_required
def convocatorias(request):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = Solicitante.objects.get(pk=request.user.id)
    #obtener modalidades que le corresponden al usuario
    if solicitante.es_renovacion:
        modalidades = Modalidad.objects.filter(mostrar=True, tipo=Modalidad.TIPO_CHOICES[0][0])
    else:
        modalidades = Modalidad.objects.filter(mostrar=True, tipo=Modalidad.TIPO_CHOICES[1][0])
    convocatoria = Convocatoria.objects.all().first()
    fecha_convocatoria = convocatoria.fecha_convocatoria if convocatoria else False
    solicitud = Solicitud.objects.filter(solicitante = solicitante, ciclo = ciclo_actual()).first()    
    
    context = {
        'convocatoria': convocatoria,
        'ciclo_actual': ciclo_actual(),
        'modalidades' : modalidades,        
        'solicitud_existe' : solicitud,
        'solicitante' : solicitante,
        'fecha_convocatoria': fecha_convocatoria
    }    
    return render(request, 'usuario_solicitud/convocatorias.html', context)

def notificar_si_falta_documentos(solicitud):
    documentos_modalidad = solicitud.modalidad.documento_set.all()
    respuestas_documentos_solicitud = RespuestaDocumento.objects.filter(solicitud=solicitud) 
    #si no hay el mismo numero de documentos que de respuesta enviar la notificacion
    if set(documentos_modalidad) != set({resp.documento for resp in respuestas_documentos_solicitud}):        
        notif.nueva(solicitud.solicitante, 'Falta uno o mas documentos requeridos en su solicitud. Favor de revisar su solicitud', 'solicitudes:documentos_convocatoria', urlArgs=[solicitud.modalidad_id])
        solicitud.estado=Solicitud.ESTADO_CHOICES[1][0]
        solicitud.save()
        return True
    else:
        return False

@login_required
def documentos_convocatorias(request, modalidad_id):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url: 
        return redirect(url)
        
    solicitante = solicitante.solicitante
    modalidad = get_object_or_404(Modalidad, pk=modalidad_id)
    documentos = Documento.objects.filter(modalidad__id=modalidad_id)
    try:
        solicitud = Solicitud.objects.get(solicitante=solicitante, modalidad=modalidad, ciclo=ciclo_actual())        
    except Solicitud.DoesNotExist:
        solicitud = Solicitud(modalidad=modalidad, solicitante=solicitante, ciclo=ciclo_actual())
    otra_solicitud_existe = Solicitud.objects.filter(solicitante = solicitante, ciclo = ciclo_actual()).exists()
    convocatoria = Convocatoria.objects.all().first()

    #verificar casos donde el usuario no deberia estar en esta vista
    #el usuario ya tiene otra solicitud en otra convocatoria
    if not solicitud.id and otra_solicitud_existe:
        solicitudExistente = Solicitud.objects.get(solicitante=solicitante, ciclo = ciclo_actual())
        messages.warning(request, f'Ya estás participando en la modalidad de {solicitudExistente.modalidad.nombre}.')
        return redirect('solicitudes:convocatorias')
    #no hay ninguna convocatoria activa
    elif not solicitud.id and not convocatoria.fecha_convocatoria:
        messages.warning(request, f'La convocatoria no esta activa.')
        return redirect('solicitudes:convocatorias')
    #no le corresponde esa modalidad de ingrego o reingreso
    elif (modalidad.tipo == Modalidad.TIPO_CHOICES[0][0] and not solicitante.es_renovacion) or (modalidad.tipo == Modalidad.TIPO_CHOICES[1][0] and solicitante.es_renovacion):
        messages.warning(request, f'No tiene los permisos correctos para ingresar a esa modalidad.')
        return redirect('solicitudes:convocatorias')

    if request.method == 'GET':    
        listaDocumentos = []
        for documento in documentos:
            try:
                instance = RespuestaDocumento.objects.get(solicitud=solicitud, documento=documento)
                form = DocumentoRespForm(instance=instance, prefix=documento.id)
            except RespuestaDocumento.DoesNotExist:
                instance = RespuestaDocumento(solicitud=solicitud, documento=documento)
                form = DocumentoRespForm(instance=instance, prefix=documento.id)
            tupla = (documento, form)
            listaDocumentos.append(tupla)            

    if request.method == 'POST':                
        listaDocumentos = []
        for documento in documentos:            
            try:
                instance = RespuestaDocumento.objects.get(solicitud=solicitud, documento=documento)
                form = DocumentoRespForm(request.POST, request.FILES, instance=instance, prefix=documento.id)
            except RespuestaDocumento.DoesNotExist:
                instance = RespuestaDocumento(solicitud=solicitud, documento=documento)
                form = DocumentoRespForm(request.POST, request.FILES, instance=instance, prefix=documento.id)
            tupla = (documento, form)
            listaDocumentos.append(tupla)  
        
        #si ya existe una solicitud y no es esta
        if (not solicitud.id) and otra_solicitud_existe:
            pass
        else:
            todoValido = True
            for documento, respDocForm in listaDocumentos:
                if not respDocForm.is_valid():
                    todoValido = False
                    messages.error(request, respDocForm.errors)
                else:
                    if not solicitud.id:
                        solicitud.save()
                    if respDocForm.instance.id and respDocForm.instance.file is not None:                                                
                        oldFile = RespuestaDocumento.objects.get(id=respDocForm.instance.id).file
                        if respDocForm.instance.file != oldFile:                            
                            oldFile.delete()                            
                    respDocForm.save()
            if todoValido:                
                messages.success(request, "Solicitud enviada con éxito.")
                return redirect("solicitudes:convocatorias")
            if solicitud.id:
                notificar_si_falta_documentos(solicitud)

    context ={
        'solicitud': solicitud,
        'modalidad': modalidad,
        'listaDocumentos': listaDocumentos,
        'convocatoria': convocatoria,
        'otra_solicitud_existe': otra_solicitud_existe
    }

    #si ya existe la solicitud se muestra la vista para modificar los documentos
    print(solicitud.id)
    if solicitud.id:
        return render(request, 'usuario_solicitud/modificar_docs_convocatoria.html', context)    
    #si no existe la solicitud se muestra la vista para crear la solicitud
    else:
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
