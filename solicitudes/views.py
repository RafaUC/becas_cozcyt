from django.shortcuts import render, get_object_or_404
import os
from django.http import FileResponse
from usuarios.models import Solicitante
from .models import RespuestaDocumento
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
    solicitanteU = get_object_or_404(Solicitante, pk = soli)    
    if(documentoRespuesta.solicitante == solicitanteU):
        raise Http404("El recurso no existe")
    response = FileResponse(documentoRespuesta.pdf)
    return response