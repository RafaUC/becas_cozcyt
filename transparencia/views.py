from django.shortcuts import render
from solicitudes.models import getListaCiclos


def getContextoBaseTransparencia(request):    
    ciclosPrevios = getListaCiclos()[:2]    
    context = {
        'ciclosPrevios': ciclosPrevios
    }
    return context


def inicioTransparencia(request):
    
    context = {

    }
    context.update(getContextoBaseTransparencia(request))
    return render(request, 'base_transparencia.html', context)


def resultados(request, num):    
    #solo obtenemos los ultimos 2 ciclos
    ciclosPrevios = getListaCiclos()[:2]     
    
    ciclo = ciclosPrevios[0]    
    try:
        if num > 0:
            ciclo = ciclosPrevios[num]
    except IndexError:
        pass
    print(ciclo)


    context = {
        'ciclo': ciclo
    }
    context.update(getContextoBaseTransparencia(request))
    return render(request, 'resultados.html', context)