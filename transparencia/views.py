from django.shortcuts import render
from solicitudes.models import getListaCiclos
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
    context = {
    'ciclo': ciclo
    }

    context.update(getContextoBaseTransparencia(request)) #permi
    return render(request, 'inicio.html', context)