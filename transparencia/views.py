from django.shortcuts import render
from solicitudes.models import getListaCiclos
from .forms import ModalidadSelectForm
from modalidades.models import Modalidad, Convocatoria, ciclo_actual
from solicitudes.models import Solicitud


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


def resultadosValidarCiclo(request,num):
    #solo obtenemos los ultimos 2 ciclos
    ciclosPrevios = getListaCiclos()[:2]     
        
    ciclo = ciclosPrevios[0]    
    try:
        if num > 0:
            ciclo = ciclosPrevios[num]
    except IndexError:
        pass  
    return ciclo

def resultados(request, num):    
    ciclo = resultadosValidarCiclo(request, num)    

    context = {
        'ciclo': ciclo,        
    }
    context.update(getContextoBaseTransparencia(request))
    return render(request, 'resultados.html', context)


def resultadosContenido(request,num,mod):
    ciclo = resultadosValidarCiclo(request, num)    

    convocatoria = Convocatoria.objects.all().first() #Obtiene la convocatoria    
    cicloAct = ciclo_actual()
    #si el ultimo siclo publicado no coincide con el actual y el seleccionado es el actual, siginifica que no esta publicado
    if convocatoria.ultimo_ciclo_publicado != cicloAct and ciclo == cicloAct:
        folios = []
        titulo = "Los resultados de la convocatoria todavía no se han publicado."
        modalidadSelectForm = None
    else:
        modalidad = Modalidad.objects.filter(id=mod, mostrar=True).first()    
        if not modalidad:
            modalidad = Modalidad.objects.filter(mostrar=True).first()    
        modalidadSelectForm = ModalidadSelectForm(initial={'modalidad': mod})

        #obtener solicitudes aceptadas
        solicitudes = Solicitud.objects.filter(ciclo=ciclo, modalidad=modalidad, estado=Solicitud.ESTADO_CHOICES[3][0]).select_related('solicitante').order_by('solicitante_id')
        folios = [solicitud.solicitante.folio for solicitud in solicitudes]
        titulo = modalidad

    context = {
        'folios': folios,
        'titulo': titulo,
        'modalidadSelectForm': modalidadSelectForm,
    }
    return render(request, 'resultadosContenido.html', context)


def transparenciaSIT(request):

    context = {

    }
    context.update(getContextoBaseTransparencia(request))
    return render(request, 'transparenciaSIT.html', context)