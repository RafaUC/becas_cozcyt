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
    request.session['anterior'] = request.build_absolute_uri()       
    solicitudes = Solicitud.objects.all()   

    if request.method == 'GET':
        search_query = request.GET.get('search', '')    
        #Si se hizo una busqueda de filtrado     
        if search_query:                                      
            solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query)      

    paginator = Paginator(solicitudes, 20)  # Mostrar 10 ins por página
    page_number = request.GET.get('page')
    page_soli = paginator.get_page(page_number)

    context = {
        'ciclo' : cicloActual,
        'page_soli': page_soli
    }    
    return render(request, 'admin/solicitudes.html', context)