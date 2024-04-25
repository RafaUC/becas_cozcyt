from django.shortcuts import render
from solicitudes.models import getListaCiclos

from modalidades.forms import *
from modalidades.models import ciclo_actual


def getContextoBaseTransparencia(request):    
    ciclosPrevios = getListaCiclos()[:2]
    print(ciclosPrevios)
    context = {
        'ciclosPrevios': ciclosPrevios
    }
    return context

# Create your views here.
def inicioTransparencia(request):
    ciclo = ciclo_actual
    convocatoria = Convocatoria.objects.all().first()
    fecha_convocatoria = convocatoria.fecha_convocatoria if convocatoria else False
    context = {
    'ciclo': ciclo,
    'convocatoria':convocatoria,
    'fecha_convocatoria': fecha_convocatoria
    }

    context.update(getContextoBaseTransparencia(request)) #permi
    return render(request, 'inicio.html', context)