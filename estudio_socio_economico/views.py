from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.conf import settings
from usuarios.views import verificarRedirect
from usuarios.models import Usuario, Solicitante
from .models import Seccion, Elemento, Opcion

# Create your views here.

@login_required
def estudioSE(request):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE
    preguntasEstudio = Seccion.objects.prefetch_related('elemento_set__opcion_set').all()
        
    #inicializar los forms de respuestas


    return render(request, 'solicitante/estudioSE.html')