from django.shortcuts import render, get_object_or_404, redirect
import os
from django.http import FileResponse
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from usuarios.views import verificarRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods



from usuarios.models import Usuario, Solicitante
from .models import Notificacion
from . import notificaciones as notif

# Create your views here.

@require_http_methods(["GET"])
def numNotifNL(request):
    # Lógica para contar los mensajes no leídos (ajusta según tu modelo)
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    notificaciones = Notificacion.objects.filter(solicitante=solicitante) 
    numero_mensajes_no_leidos = 0
    for notificacion in notificaciones:
        if notificacion.leido:            
            break
        else:            
            numero_mensajes_no_leidos += 1


    # Devuelve la respuesta como JSON
    return JsonResponse({'numero_mensajes_no_leidos': numero_mensajes_no_leidos})


def renderNotificaciones(request):
    solicitante = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(solicitante)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    page = request.GET.get('page', 1)    
    notificaciones = Notificacion.objects.filter(solicitante=solicitante)    
    paginator = Paginator(notificaciones, 12)
    currentPage = paginator.get_page(page)
    if currentPage.has_next():
        next_page_number = currentPage.next_page_number()
    else:
        next_page_number = None


    context = {
        'currentPage': currentPage
    }        
    data = {
        'html_response': render(request, 'content_notif.html', context).content.decode('utf-8'),
        'next_page': next_page_number,
    }    
    return JsonResponse(data)

@require_POST
def marcar_notificacion_leida(request):
    notification_id = request.POST.get('notification_id')
    notification = get_object_or_404(Notificacion, id=notification_id)
    
    # Marcar la notificación como leída
    notification.leido = True
    notification.save()

    return JsonResponse({'status': 'ok'})
