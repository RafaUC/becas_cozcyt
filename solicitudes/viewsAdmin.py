from django.shortcuts import render, get_object_or_404
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator


from usuarios.views import verificarRedirect
from usuarios.viewsAdmin import BusquedaEnCamposQuerySet
from usuarios.models import Usuario
from modalidades.models import ciclo_actual
from .forms import FiltroForm
from modalidades.models import Modalidad
from .models import *

from usuarios.models import Solicitante

# Create your views here.
#########################################
# Nota: Recordar
#no cache a las subidas al servidor
##########################################

@login_required
def estadisticas(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'estadisticas/estadisticas.html')

@login_required
def historialSolicitante(request, pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=pk)  
    solicitudes = Solicitud.objects.filter(solicitante = solicitante)

    context = {
        'solicitudes': solicitudes,
        'solicitante': solicitante
    }

    return render(request, 'admin/historialSolicitante.html', context)

@login_required
def listaSolicitudes(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    cicloActual = ciclo_actual()
    request.session['anterior'] = request.get_full_path()        
    url_base_page = request.session['anterior'].split('&page=')[0]
    url_base_page = url_base_page.split('?')[1] if '?' in url_base_page else ''    
    solicitudes = Solicitud.objects.filter(ciclo = cicloActual)  
    modalidades = Modalidad.objects.all()
    filtroSolForm = FiltroForm(prefix='filtEst', nombre='Estado Solicitud', choices=Solicitud.ESTADO_CHOICES, selectedAll=False)
    filtroModForm = FiltroForm(prefix='filtMod', nombre='Modalidad', queryset=modalidades, to_field_name='nombre', selectedAll=False)

    if 'search' in request.GET:
        filtroSolForm = FiltroForm(request.GET,search_query_name='~estado', prefix='filtEst', nombre='Estado Solicitud', choices=Solicitud.ESTADO_CHOICES, selectedAll=False)
        filtroModForm = FiltroForm(request.GET,search_query_name='~modalidad__id', prefix='filtMod', nombre='Modalidad', queryset=modalidades, to_field_name='nombre', selectedAll=False)                               
                                
        search_query = filtroSolForm.get_search_query()
        solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query) #filtra por el primer filtro
        search_query = filtroModForm.get_search_query()
        solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query) #filtra por el segundo filtro
        search_query = request.GET.get('search', '')    
        
        #Si se hizo una busqueda de filtrado     
        if search_query:       
            solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query)      

    if request.method == 'POST':
        soliToUpdate = solicitudes        
        accion = None
        todo = None
        seleccion = None
        if 'boton-presionado' in request.POST:
            accion = request.POST['boton-presionado']
        if 'select-todo-check' in request.POST:
            todo = request.POST['select-todo-check']
        if 'select-soli-check' in request.POST:
            seleccion = request.POST.getlist('select-soli-check')
            seleccion = [int(id_str) for id_str in seleccion]
        print(f'{accion} - {todo} - {seleccion}')
        #print(f'{type(accion)} - {type(todo)} - {type(seleccion)}')

        if accion and seleccion:            
            if todo:
                soliToUpdate = soliToUpdate.exclude(estado=Solicitud.ESTADO_CHOICES[0][0])                
                soliToUpdate = soliToUpdate.exclude(estado=Solicitud.ESTADO_CHOICES[1][0])  
                if accion == 'aceptar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[3][0])
                    messages.success(request, f'Se aceptaron todas las {soliToUpdate.count()} solicitudes filtradas con éxito')
                elif accion == 'rechazar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[4][0])
                    messages.success(request, f'Se rechazaron todas las {soliToUpdate.count()} solicitudes filtradas con éxito')
            else:
                soliToUpdate = soliToUpdate.filter(id__in=seleccion)                
                if accion == 'aceptar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[3][0])
                    messages.success(request, f'Se aceptaron las {soliToUpdate.count()} solicitudes seleccionadas con éxito')    
                elif accion == 'rechazar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[4][0])
                    messages.success(request, f'Se rechazaron las {soliToUpdate.count()} solicitudes seleccionadas con éxito')    
        else:
            messages.error(request, 'No se seleccionaron solicitudes')    

                    
    paginator = Paginator(solicitudes, 20)  # Mostrar 10 ins por página
    page_number = request.GET.get('page')
    page_soli = paginator.get_page(page_number)

    context = {
        'ciclo' : cicloActual,
        'page_soli': page_soli,
        'url_base_page': url_base_page,
        'filtroSolForm': filtroSolForm,
        'filtroModForm': filtroModForm
    }    
    return render(request, 'admin/solicitudes.html', context)

def documentos_solicitante(request, pk):
    solicitante = get_object_or_404(Solicitante, pk=pk)  
    solicitud = Solicitud.objects.get(solicitante=solicitante, ciclo=ciclo_actual())
    modalidad = Modalidad.objects.get(pk = solicitud.modalidad.pk)
    documentos = Documento.objects.filter(modalidad=solicitud.modalidad)
    documentosResp = RespuestaDocumento.objects.filter(solicitud=solicitud)
    listaDocumentos = zip(documentos, documentosResp)
    # print(documentos)
    # print(documentosResp)
    # print(solicitud.modalidad.pk)
    context = {
        'solicitante': solicitante,
        'listaDocumentos' : listaDocumentos,
        'modalidad' : modalidad,
    }
    accion = None
    if request.method == 'POST':
        print(1)
        if 'boton-presionado' in request.POST:
            accion = request.POST['boton-presionado']
            print("boton presionado")
            print(f'{accion}')
            if accion == 'aprobado':
                print("aprobado")
        messages.success(request, "Documentos de solicitud revisados con éxito.")
    return render(request, 'admin/documentosSolicitante.html', context)