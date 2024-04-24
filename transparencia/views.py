from django.shortcuts import render
from solicitudes.models import getListaCiclos

def getContextoBaseTransparencia(request):    
    ciclosPrevios = getListaCiclos()[:2]
    print(ciclosPrevios)
    context = {
        'ciclosPrevios': ciclosPrevios
    }
    return context

# Create your views here.
def inicioTransparencia(request):
    
    context = {

    }
    context.update(getContextoBaseTransparencia(request))
    return render(request, 'base_transparencia.html', context)