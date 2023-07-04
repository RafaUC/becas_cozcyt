from django.shortcuts import render, get_object_or_404
import os
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

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