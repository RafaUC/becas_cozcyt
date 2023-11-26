from django.shortcuts import render, get_object_or_404
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


from usuarios.views import verificarRedirect
from usuarios.models import Usuario
from modalidades.models import ciclo_actual

# Create your views here.
#########################################
# Nota: Recordar
#no cache a las subidas al servidor
##########################################


@login_required
def solicitudes(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    cicloActual = ciclo_actual()

    context = {
        'ciclo' : cicloActual
    }    
    return render(request, 'admin/solicitudes.html', context)