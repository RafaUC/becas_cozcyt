from django.shortcuts import render
from solicitudes.models import getListaCiclos
from django.db.models import Count
from django.db.models import Subquery, OuterRef

from modalidades.forms import *
from solicitudes.forms import *
from solicitudes.models import *
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
    modalidades = Modalidad.objects.filter(pk__in = Modalidad.objects.values('nombre').distinct().annotate(pk = Subquery(Modalidad.objects.filter(nombre= OuterRef("nombre")).order_by("pk").values("pk")[:1])).values_list("pk", flat=True))
    fecha_convocatoria = convocatoria.fecha_convocatoria if convocatoria else False
    
    context = {
    'ciclo': ciclo,
    'convocatoria':convocatoria,
    'fecha_convocatoria': fecha_convocatoria,
    'modalidades': modalidades
    }

    context.update(getContextoBaseTransparencia(request)) #permi
    return render(request, 'inicio.html', context)