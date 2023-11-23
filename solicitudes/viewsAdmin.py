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


