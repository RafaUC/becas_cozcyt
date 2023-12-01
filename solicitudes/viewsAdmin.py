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
from .models import Solicitud

# Create your views here.
#########################################
# Nota: Recordar
#no cache a las subidas al servidor
##########################################


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

    if request.method == 'GET':             
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