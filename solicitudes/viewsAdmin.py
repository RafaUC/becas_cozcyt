from django.shortcuts import render, get_object_or_404
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponse
from django.http import FileResponse
from .models import RespuestaDocumento, Solicitud
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
import colorsys
from django.db.models import Count


from usuarios.views import verificarRedirect
from usuarios.viewsAdmin import BusquedaEnCamposQuerySet
from usuarios.models import Usuario, Institucion, Carrera, Municipio
from modalidades.models import ciclo_actual
from .forms import FiltroForm
from modalidades.models import Modalidad
from .models import *

from usuarios.models import Solicitante

# Create your views here.
#########################################
# Nota: Recordar
#no cache a las subidas al servidor
##########################################

def GeneradorColores(color_inicial, incremento_luminosidad, min_luminosidad, max_luminosidad, incremento_hue):
    """
    Genera colores a partir de un color inicial, ajustando luminosidad y tono.
    
    :param color_inicial: Tupla (r, g, b) con valores en el rango [0, 255].
    :param incremento_luminosidad: Incremento/decremento en la luminosidad en el rango [-1, 1].
    :param limite_luminosidad: Límite de la luminosidad antes de cambiar el tono.
    :param incremento_hue: Incremento/decremento en el tono en el rango [-1, 1].
    :return: Generador de colores (tuplas) en formato (r, g, b).
    """
    r, g, b = color_inicial

    while True:        
        # Convertir RGB a HSL
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

        # Ajustar luminosidad y hue
        l += incremento_luminosidad
        h += incremento_hue

        # Verificar límites de luminosidad
        if l < min_luminosidad:            
            l = max_luminosidad - (min_luminosidad-l) 
            if l < min_luminosidad:
                l = min_luminosidad            
        elif l > max_luminosidad:            
            l = min_luminosidad + (l-max_luminosidad)
            if l > max_luminosidad:
                l = max_luminosidad
                    
        h += incremento_hue
        # Verificar límite de tono (Hue)
        if h > 1.0 or h < 0.0:
            h %= 1.0

        s = l

        # Convertir HSL a RGB
        r, g, b = [int(x * 255.0) for x in colorsys.hls_to_rgb(h, l, s)]        
        yield r, g, b



@login_required
def estadisticas(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    colorInicial = (190, 70, 53)  # Color inicial en formato RGB
    incrementoIuminosidad = 0.1  # Incremento/decremento en la luminosidad
    minLuminosidad = 0.8  # Límite de la luminosidad antes de cambiar el tono
    maxLuminosidad = 0.8  # Límite de la luminosidad antes de cambiar el tono    
    incrementoHue = 0.03  # Incremento/decremento en el tono
    
    solicitudes = Solicitud.objects.filter(ciclo=ciclo_actual()).select_related('solicitante__municipio')
    municipiosParticipando = solicitudes.values('solicitante__municipio__id').distinct().count()

    tarjetasEstadisticas = [ #Lista de diccionarios que contienen la informacion de las tarjetas de cada estadistica
        {
            'titulo': 'Solicitudes recibidas',
            'iconCSS': 'fa-inbox',
            'valor': solicitudes.count(),
            'url': 'solicitudes:ESolicitudes'
        },
        {
            'titulo': 'Modalidades',
            'iconCSS': 'fa-object-group',
            'valor': Modalidad.objects.all().count(),
            'url': 'solicitudes:ESolicitudes'
        },
        {
            'titulo': 'Instituciones registradas',
            'iconCSS': 'fa-object-group',
            'valor': Institucion.objects.all().count(),
            'url': 'solicitudes:ESolicitudes'
        },
        {
            'titulo': 'Carreras registradas',
            'iconCSS': 'fa-object-group',
            'valor': Carrera.objects.all().count(),
            'url': 'solicitudes:ESolicitudes'
        },        
        {
            'titulo': 'Municipios participantes',
            'iconCSS': 'fa-object-group',
            'valor': municipiosParticipando,
            'url': 'solicitudes:ESolicitudes'
        },
        
    ]

    # Asignar los colores de fondo
    generadorColores = GeneradorColores(colorInicial, incrementoIuminosidad, minLuminosidad, maxLuminosidad, incrementoHue)    
    for tarjetaDict in tarjetasEstadisticas:
        tarjetaDict['rgb'] = next(generadorColores)

    context = {
        'tarjetasEstadisticas': tarjetasEstadisticas
    }
    
    return render(request, 'estadisticas/estadisticas.html', context)


def estadisticaSolicitudes(request):
    url = verificarRedirect(request.user, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)

    #config colores
    colorInicial = (1, 0, 0)  # Color inicial en formato RGB
    incrementoIuminosidad = 0.06  # Incremento/decremento en la luminosidad
    minLuminosidad = 0.35  # Límite de la luminosidad antes de cambiar el tono
    maxLuminosidad = 0.75  # Límite de la luminosidad antes de cambiar el tono    
    incrementoHue = 0.011  # Incremento/decremento en el tono

    conjuntosEstadisticos = []
    valoresFrecuencias = Solicitud.objects.values('estado').annotate(frecuencia=Count('estado'))
    valoresFrecuencias = sorted(valoresFrecuencias, key=lambda x: x['frecuencia'], reverse=True)
    labels = [dict(Solicitud.ESTADO_CHOICES).get(item['estado'], item['estado']) for item in valoresFrecuencias ]    
    data = [item['frecuencia'] for item in valoresFrecuencias]
    dataLabel = 'Solicitudes'

    '''
    import random
    labels = [f"label {i + 1}" for i in range(50)]    
    data = [random.randint(1, 100) for _ in range(50)]
    data = sorted(data, reverse=True)
    #'''

    generadorColores = GeneradorColores(colorInicial, incrementoIuminosidad, minLuminosidad, maxLuminosidad, incrementoHue)    
    listaColores = [next(generadorColores) for _ in data]

    conjuntoEst = {
        'grafico': {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': dataLabel,
                    'data': data,
                    'backgroundColor': [f'rgba({r}, {g}, {b}, 1)' for r, g, b in listaColores], 
                    'borderColor': 'rgba(255,255,255,0.2)', 
                    'borderWidth': 2,
                    'hoverOffset': 20,
                }]
            },
            'options': {
                'plugins': {
                    'legend': {
                        'display': False
                    }, 
                },
                'layout': {
                    'padding': 10
                }               
            }
        }
    }
    conjuntosEstadisticos.append(conjuntoEst)

    context = {
        'conjuntosEstadisticos': conjuntosEstadisticos
    }
    
    return render(request, 'estadisticas/eSolicitudes.html', context)


@login_required
def historialSolicitante(request, pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=pk)  
    solicitudes = Solicitud.objects.filter(solicitante = solicitante).order_by('-id')

    context = {
        'solicitudes': solicitudes,
        'solicitante': solicitante
    }

    return render(request, 'admin/historialSolicitante.html', context)

@login_required
def listaSolicitudes(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    cicloActual = ciclo_actual()
    request.session['anterior'] = request.get_full_path()        
    url_base_page = request.session['anterior'].split('&page=')[0]
    url_base_page = url_base_page.split('?')[1] if '?' in url_base_page else ''    
    solicitudes = Solicitud.objects.filter(ciclo = cicloActual)  
    modalidades = Modalidad.objects.all()
    filtroSolForm = FiltroForm(prefix='filtEst', nombre='Estado Solicitud', choices=Solicitud.ESTADO_CHOICES, selectedAll=False)
    filtroModForm = FiltroForm(prefix='filtMod', nombre='Modalidad', queryset=modalidades, to_field_name='nombre', selectedAll=False)

    if 'search' in request.GET:
        filtroSolForm = FiltroForm(request.GET,search_query_name='~estado', prefix='filtEst', nombre='Estado Solicitud', choices=Solicitud.ESTADO_CHOICES, selectedAll=False)
        filtroModForm = FiltroForm(request.GET,search_query_name='~modalidad__id', prefix='filtMod', nombre='Modalidad', queryset=modalidades, to_field_name='nombre', selectedAll=False)                               
                                
        search_query = filtroSolForm.get_search_query()
        solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query) #filtra por el primer filtro
        search_query = filtroModForm.get_search_query()
        solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query) #filtra por el segundo filtro
        search_query = request.GET.get('search', '')    
        
        #Si se hizo una busqueda de filtrado     
        if search_query:       
            solicitudes = BusquedaEnCamposQuerySet(solicitudes, search_query)      

    if request.method == 'POST':
        soliToUpdate = solicitudes        
        accion = None
        todo = None
        seleccion = None
        if 'boton-presionado' in request.POST:
            accion = request.POST['boton-presionado']
        if 'select-todo-check' in request.POST:
            todo = request.POST['select-todo-check']
        if 'select-soli-check' in request.POST:
            seleccion = request.POST.getlist('select-soli-check')
            seleccion = [int(id_str) for id_str in seleccion]
        print(f'{accion} - {todo} - {seleccion}')
        #print(f'{type(accion)} - {type(todo)} - {type(seleccion)}')

        if accion and seleccion:            
            if todo:
                soliToUpdate = soliToUpdate.exclude(estado=Solicitud.ESTADO_CHOICES[0][0])                
                soliToUpdate = soliToUpdate.exclude(estado=Solicitud.ESTADO_CHOICES[1][0])  
                if accion == 'aceptar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[3][0])
                    messages.success(request, f'Se aceptaron todas las {soliToUpdate.count()} solicitudes filtradas con éxito')
                elif accion == 'rechazar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[4][0])
                    messages.success(request, f'Se rechazaron todas las {soliToUpdate.count()} solicitudes filtradas con éxito')
            else:
                soliToUpdate = soliToUpdate.filter(id__in=seleccion)                
                if accion == 'aceptar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[3][0])
                    messages.success(request, f'Se aceptaron las {soliToUpdate.count()} solicitudes seleccionadas con éxito')    
                elif accion == 'rechazar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[4][0])
                    messages.success(request, f'Se rechazaron las {soliToUpdate.count()} solicitudes seleccionadas con éxito')    
        else:
            messages.error(request, 'No se seleccionaron solicitudes')    

                    
    paginator = Paginator(solicitudes, 20)  # Mostrar 10 ins por página
    page_number = request.GET.get('page')
    page_soli = paginator.get_page(page_number)

    context = {
        'ciclo' : cicloActual,
        'page_soli': page_soli,
        'url_base_page': url_base_page,
        'filtroSolForm': filtroSolForm,
        'filtroModForm': filtroModForm
    }    
    return render(request, 'admin/solicitudes.html', context)

def documentos_solicitante(request, pk):
    solicitante = get_object_or_404(Solicitante, pk=pk)  
    solicitud = Solicitud.objects.get(solicitante=solicitante, ciclo=ciclo_actual())
    modalidad = Modalidad.objects.get(pk = solicitud.modalidad.pk)
    documentos = Documento.objects.filter(modalidad=solicitud.modalidad)
    documentosResp = RespuestaDocumento.objects.filter(solicitud=solicitud)
    listaDocumentos = zip(documentos, documentosResp)
    # print(documentos)
    # print(documentosResp)
    # print(solicitud.modalidad.pk)
    context = {
        'solicitante': solicitante,
        'listaDocumentos' : listaDocumentos,
        'modalidad' : modalidad,
    }

    if request.method == 'POST':
        seleccionAceptados = None
        seleccionDenegados = None
        if 'estado-boton-aceptado' in request.POST:
            seleccionAceptados = request.POST.getlist('estado-boton-aceptado')
            seleccionAceptados = [int(id_str) for id_str in seleccionAceptados]
        if 'estado-boton-denegado' in request.POST:
            seleccionDenegados = request.POST.getlist('estado-boton-denegado')
            seleccionDenegados = [int(id_str) for id_str in seleccionDenegados]
            print(f'{seleccionDenegados}')

        #**Hacer una condicional para que el estado de la solicitud no cambie a documentación aprobada, cuando hay documentos denegados**
        #Existieron documentos con error y otros fueron aprobados
        if seleccionDenegados != None and seleccionAceptados != None: 
            docsAceptadosToUpdate = documentosResp.filter(id__in = seleccionAceptados)   
            docsAceptadosToUpdate.update(estado=RespuestaDocumento.ESTADO_CHOICES[1][0])
            docsDenegadosToUpdate = documentosResp.filter(id__in = seleccionDenegados)
            docsDenegadosToUpdate.update(estado=RespuestaDocumento.ESTADO_CHOICES[2][0])
            solicitud.estado = Solicitud.ESTADO_CHOICES[1][0]
            solicitud.save()

        #Todos los documentos fueron denegados
        if seleccionAceptados == None:
            docsDenegadosToUpdate = documentosResp.filter(id__in = seleccionDenegados)
            docsDenegadosToUpdate.update(estado=RespuestaDocumento.ESTADO_CHOICES[2][0])
            messages.success(request, f'Se aceptaron las {docsDenegadosToUpdate.count()} solicitudes seleccionadas con éxito')
            solicitud.estado = Solicitud.ESTADO_CHOICES[1][0]
            solicitud.save()
            
        #Todos los documentos fueron aceptados
        if seleccionDenegados == None: 
            docsAceptadosToUpdate = documentosResp.filter(id__in = seleccionAceptados)   
            docsAceptadosToUpdate.update(estado=RespuestaDocumento.ESTADO_CHOICES[1][0])
            solicitud.estado = Solicitud.ESTADO_CHOICES[2][0]
            solicitud.save()
            print(solicitud.estado)
            
        
        messages.success(request, "Documentos de solicitud revisados con éxito.")
        return redirect("solicitudes:ASolicitudes")
    return render(request, 'admin/documentosSolicitante.html', context)