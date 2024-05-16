from django.shortcuts import render
from solicitudes.models import getListaCiclos
from django.db.models import Count
from django.db.models import Subquery, OuterRef

from modalidades.forms import *
from solicitudes.forms import *
from solicitudes.models import *
from .forms import ModalidadSelectForm
from modalidades.models import Modalidad, Convocatoria, Ciclo
from solicitudes.models import Solicitud


def getContextoBaseTransparencia(request):    
    ciclosPrevios = getListaCiclos()[:2]    
    context = {
        'ciclosPrevios': ciclosPrevios
    }
    return context


def inicioTransparencia(request):
    ciclo = ciclo_actual()
    convocatoria = Convocatoria.get_object()
    modalidades = Modalidad.objects.filter(mostrar=True, archivado=False, pk__in = Modalidad.objects.values('nombre').distinct().annotate(pk = Subquery(Modalidad.objects.filter(nombre= OuterRef("nombre")).order_by("pk").values("pk")[:1])).values_list("pk", flat=True))
    fecha_convocatoria = convocatoria.fecha_convocatoria if convocatoria else False
    
    context = {
    'ciclo': ciclo,
    'convocatoria':convocatoria,
    'fecha_convocatoria': fecha_convocatoria,
    'modalidades': modalidades
    }
    context.update(getContextoBaseTransparencia(request))
    return render(request, 'inicio.html', context)


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

    convocatoria = Convocatoria.get_object() #Obtiene la convocatoria    
    cicloAct = ciclo_actual()
    #si el ultimo siclo publicado no coincide con el actual y el seleccionado es el actual, siginifica que no esta publicado
    if convocatoria.ultimo_ciclo_publicado != cicloAct and ciclo == cicloAct:
        folios = []
        titulo = "Los resultados de la convocatoria todavía no se han publicado."
        modalidadSelectForm = None
    else:
        modalidadesdelCiclo = MontoModalidad.objects.filter(ciclo=ciclo).values_list('modalidad_id', flat=True).distinct()                     
        modalidad = Modalidad.objects.filter(id__in=modalidadesdelCiclo, id=mod).first()
        if not modalidad:
            modalidad = Modalidad.objects.filter(id__in=modalidadesdelCiclo, mostrar=True, archivado=False).first()
        if modalidad:    
            mod = modalidad.id 
        else:
            mod = None
        modalidadSelectForm = ModalidadSelectForm(ciclo=ciclo, initial={'modalidad': mod})
        modNombre = None
        if modalidad:
            modNombre = modalidad.nombre
            
        #obtener solicitudes aceptadas
        solicitudes = Solicitud.objects.filter(ciclo=ciclo, modalidad__nombre=modNombre, estado=Solicitud.ESTADO_CHOICES[3][0]).select_related('solicitante').order_by('solicitante_id')
        folios = [solicitud.solicitante.folio for solicitud in solicitudes]
        titulo = modalidad.nombre
        print(solicitudes.count())

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
