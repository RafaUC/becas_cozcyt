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
from django.conf import settings
import colorsys
from django.db.models import Count
from zipfile import ZipFile
import uuid
from openpyxl import Workbook
from datetime import date
from collections import Counter

from usuarios.views import verificarRedirect
from usuarios.viewsAdmin import BusquedaEnCamposQuerySet
from usuarios.models import Usuario, Institucion, Carrera, Municipio
from modalidades.models import ciclo_actual
from .forms import FiltroForm, EstadInfoSelectForm
from modalidades.models import Modalidad
from .models import *

from usuarios.models import Solicitante
from .views import notificar_si_falta_documentos

from mensajes import notificaciones as notif
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

ESTADISTICAS_SOLICITUD_EXTRA_CHOICES = [
        ('genero','Genero'),
        ('instituciones', 'Instituciones'),
        ('carreras', 'Carreras'),
        ('estado', 'Estado'),
        ('municipio', 'Municipio')
    ]

@login_required
def estadisticas(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    colorInicial = (190, 70, 53)  # Color inicial en formato RGB
    incrementoIuminosidad = 0.06  # Incremento/decremento en la luminosidad
    minLuminosidad = 0.8  # Límite de la luminosidad antes de cambiar el tono
    maxLuminosidad = 0.8  # Límite de la luminosidad antes de cambiar el tono    
    incrementoHue = 0.016  # Incremento/decremento en el tono
    
    solicitudes = Solicitud.objects.filter(ciclo=ciclo_actual()).select_related('solicitante__municipio')
    municipiosParticipando = solicitudes.values('solicitante__municipio__id').distinct().count()

    tarjetasEstadisticas = [ #Lista de diccionarios que contienen la informacion de las tarjetas de cada estadistica
        {            
            'titulo': 'Solicitudes recibidas',
            'iconCSS': 'fa-inbox',
            'valor': solicitudes.count(),
            'url': 'solicitudes:ESolicitudes',
            'getData': f'?campo_estadistica=ciclo&estadistica_filtro=Todos'
        },        
        {
            'titulo': 'Modalidades activas',
            'iconCSS': 'fa-object-group',
            'valor': Modalidad.objects.filter(mostrar = True).values('nombre').distinct().count(),
            'url': 'solicitudes:ESolicitudes',
            'getData': f'?campo_estadistica=modalidad&estadistica_filtro={ciclo_actual()}'
        },   
        {
            'titulo': 'Instituciones registradas',
            'iconCSS': 'fa-university',
            'valor': Institucion.objects.all().count(),
            'url': 'solicitudes:ESolicitudes',
            'getData': f'?campo_estadistica={ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[1][0]}&estadistica_filtro={ciclo_actual()}'
        },
        {
            'titulo': 'Carreras registradas',
            'iconCSS': 'fa-graduation-cap',
            'valor': Carrera.objects.all().count(),
            'url': 'solicitudes:ESolicitudes',
            'getData': f'?campo_estadistica={ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[2][0]}&estadistica_filtro={ciclo_actual()}'
        },        
        {
            'titulo': 'Municipios participantes',
            'iconCSS': 'fa-map-marker',
            'valor': municipiosParticipando,
            'url': 'solicitudes:ESolicitudes',
            'getData': f'?campo_estadistica={ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[4][0]}&estadistica_filtro={ciclo_actual()}'
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

def crearDictGrafica(labels=[], dataLabel='', data=[], listaColores=[],type='bar',minRotationLabel=0):        
    # Verificar si hay más de 15 elementos y combinar los demás en un elemento "otros"
    numValMax = 10
    if len(labels) > numValMax:
        otros_labels = ['Otros']
        otros_data = [sum(data[numValMax:])]
        otros_color = (100,100,100)  # Puedes ajustar este color según tus necesidades
        labels = labels[:numValMax] + otros_labels
        data = data[:numValMax] + otros_data
        listaColores = listaColores[:numValMax] + [otros_color]

    conjuntoEst = {
        'grafico': {
            'type': type,
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
                },
                'scales': {
                    'x': {
                        'ticks': {
                            'maxRotation': 90,
                            'minRotation': minRotationLabel
                        }
                    }
                }               
            }
        }
    }
    return conjuntoEst

@login_required
def estadisticaSolicitudes(request):
    url = verificarRedirect(request.user, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)

    estadistica_filtro = request.GET.get('estadistica_filtro', ciclo_actual())
    campo_estadistica = request.GET.get('campo_estadistica', 'modalidad')    
    campo_estadistica_original = campo_estadistica
    
    if request.GET:
        estadSelectForm = EstadInfoSelectForm(
            request.GET, 
            modelo_filtro=Solicitud, 
            campo_filtro='ciclo', 
            campo_estadistica_modelo=Solicitud,
            exclude_choices = ['solicitante'],
            extra_choices = ESTADISTICAS_SOLICITUD_EXTRA_CHOICES,
            initial={'estadistica_filtro': estadistica_filtro,'campo_estadistica': campo_estadistica} 
        )
    else:
        estadSelectForm = EstadInfoSelectForm(
            modelo_filtro=Solicitud, 
            campo_filtro='ciclo', 
            campo_estadistica_modelo=Solicitud,
            exclude_choices = ['solicitante'],
            extra_choices = ESTADISTICAS_SOLICITUD_EXTRA_CHOICES,
            initial={'estadistica_filtro': estadistica_filtro,'campo_estadistica': campo_estadistica} 
        )

    #config colores
    colorInicial = (1, 0, 0)  # Color inicial en formato RGB
    incrementoIuminosidad = 0.06  # Incremento/decremento en la luminosidad
    minLuminosidad = 0.35  # Límite de la luminosidad antes de cambiar el tono
    maxLuminosidad = 0.75  # Límite de la luminosidad antes de cambiar el tono    
    incrementoHue = 0.011  # Incremento/decremento en el tono
    generadorColores = GeneradorColores(colorInicial, incrementoIuminosidad, minLuminosidad, maxLuminosidad, incrementoHue)    
    
    conjuntosEstadisticos = []
    dataLabel = f'Solicitudes: {campo_estadistica}'    
    #obtenemos el queryset basado en el filtro de ciclo
    if estadistica_filtro == 'Todos':
        queryset = Solicitud.objects.all()
    else:
        queryset = Solicitud.objects.filter(ciclo = estadistica_filtro)

    minRotationLabel = 0
    if campo_estadistica == ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[0][0]: #genero
        campo_estadistica = 'solicitante__genero'
    elif campo_estadistica == 'modalidad': #modalidad
        campo_estadistica = 'modalidad__nombre'
    elif campo_estadistica == 'ciclo': 
        minRotationLabel = 90
    elif campo_estadistica == ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[1][0]:  #'instituciones'
        campo_estadistica = 'solicitante__carrera__institucion__nombre'
        minRotationLabel = 90
    elif campo_estadistica == ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[2][0]:  #'carreras'
        campo_estadistica = 'solicitante__carrera__nombre'
        minRotationLabel = 90
    elif campo_estadistica == ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[3][0]:  #'estado'
        campo_estadistica = 'solicitante__municipio__estado__nombre'
        minRotationLabel = 90
    elif campo_estadistica == ESTADISTICAS_SOLICITUD_EXTRA_CHOICES[4][0]:  #'municipio'
        campo_estadistica = 'solicitante__municipio__nombre'
        minRotationLabel = 90

    
    #se seleccionan solo los valores unicos y su frecuencia
    
    if campo_estadistica == 'ciclo':
        valores = queryset.values_list(campo_estadistica, flat=True)
        frecuencias = dict(Counter(valores))         
        valores = queryset.values_list(campo_estadistica, flat=True)
        valores_unicos = []
        conjunto_vistos = set()
        for elemento in valores:
            if elemento not in conjunto_vistos:
                valores_unicos.append(elemento)
                conjunto_vistos.add(elemento)
        valoresFrecuencias = []
        for val in valores_unicos:
            valoresFrecuencias.append({campo_estadistica: val, 'frecuencia': frecuencias[val]})
    else:
        valoresFrecuencias = queryset.values(campo_estadistica).annotate(frecuencia=Count(campo_estadistica))        
        #reordenan de mayor a menor
        valoresFrecuencias = sorted(valoresFrecuencias, key=lambda x: x['frecuencia'], reverse=True)
    #se generan los labels para cada frecuencia, se intenta a ver si existe en los estados, sino se pone el valor en si
    labels = [dict(Solicitud.ESTADO_CHOICES).get(item[campo_estadistica], item[campo_estadistica]) for item in valoresFrecuencias ]    
    frecuencias = [item['frecuencia'] for item in valoresFrecuencias]
    
    listaColores = [next(generadorColores) for _ in frecuencias]

    grafica = crearDictGrafica(labels, dataLabel, frecuencias, listaColores, minRotationLabel=minRotationLabel)
    conjuntosEstadisticos.append(grafica)    

    listaColores =listaColores.copy()
    labels = labels.copy()
    frecuencias =  frecuencias.copy()
    listaColores.insert(0, (255,255,255))
    labels.insert(0, 'Total')
    frecuencias.insert(0, sum(frecuencias))
    conjuntosEstadisticos.append({
        'tipo': 'leyenda',
        'dataLabel': dataLabel,
        'data': zip(listaColores, labels, frecuencias)
    })
    
    valoresFrecuencias = queryset.filter(estado=Solicitud.ESTADO_CHOICES[3][0]).values('modalidad__nombre', 'modalidad__monto').annotate(frecuencia=Count('modalidad__nombre'))            
    valoresFrecuencias = sorted(valoresFrecuencias, key=lambda x: x['frecuencia'], reverse=True)    
    labels = [item['modalidad__nombre']+':' for item in valoresFrecuencias ]   
    total = 0       
    totales = []
    for item in valoresFrecuencias:
        totales.append( f"${(item['frecuencia'] * item['modalidad__monto']):,.2f}")
        total += item['frecuencia'] * item['modalidad__monto']
    labels.insert(0, 'Total:')
    totales.insert(0, f'${total:,.2f}')
    conjuntosEstadisticos.append({
        'tipo': 'lista',
        'dataLabel': f'Dinero invertido: {estadistica_filtro}',
        'data': zip(labels, totales)
    })
    

    context = {
        'tituloEstadistica': f'Estadística {campo_estadistica_original} del ciclo: {estadistica_filtro}',
        'urlEstaditica': 'solicitudes:ESolicitudes',
        'conjuntosEstadisticos': conjuntosEstadisticos,
        'estadSelectForm': estadSelectForm
    }
    
    return render(request, 'estadisticas/ebase.html', context)


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
    filtroModForm = FiltroForm(prefix='filtMod', nombre='Modalidad', queryset=modalidades, to_field_name='__str__', selectedAll=False)

    if 'search' in request.GET:
        filtroSolForm = FiltroForm(request.GET,search_query_name='~estado', prefix='filtEst', nombre='Estado Solicitud', choices=Solicitud.ESTADO_CHOICES, selectedAll=False)
        filtroModForm = FiltroForm(request.GET,search_query_name='~modalidad__id', prefix='filtMod', nombre='Modalidad', queryset=modalidades, to_field_name='__str__', selectedAll=False)                               
                                
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
        #print(f'{accion} - {todo} - {seleccion}')
        #print(f'{type(accion)} - {type(todo)} - {type(seleccion)}')

        if accion and seleccion:            
            if todo:
                soliToUpdate = soliToUpdate.exclude(estado=Solicitud.ESTADO_CHOICES[0][0])      
                counts = soliToUpdate.count()                          
                if accion == 'aceptar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[3][0])
                    messages.success(request, f'Se aceptaron todas las {counts} solicitudes filtradas con éxito')
                    solicitante_pk = None
                    modalidad_pk = None
                    for f in soliToUpdate.values():
                        solicitante_pk = f["solicitante_id"] 
                        modalidad_pk = f["modalidad_id"]
                        solicitante_inst = get_object_or_404(Solicitante, pk=solicitante_pk) 
                        modalidad_inst = get_object_or_404(Modalidad, pk=modalidad_pk)   
                        notif.nueva(solicitante_inst, f'Nos complace comunicarle que su solicitud para la modalidad de "{modalidad_inst.nombre}" ha sido ¡APROBADA!', 'solicitudes:historial')      
                elif accion == 'rechazar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[4][0])
                    messages.success(request, f'Se rechazaron todas las {counts} solicitudes filtradas con éxito')
                    solicitante_pk = None
                    modalidad_pk = None
                    for f in soliToUpdate.values():
                        solicitante_pk = f["solicitante_id"] 
                        modalidad_pk = f["modalidad_id"]
                        solicitante_inst = get_object_or_404(Solicitante, pk=solicitante_pk) 
                        modalidad_inst = get_object_or_404(Modalidad, pk=modalidad_pk)   
                        notif.nueva(solicitante_inst, f'Desafortunadamente su solicitud para la modalidad de "{modalidad_inst.nombre}" ha sido RECHAZADA.', 'solicitudes:historial')      
            else:
                soliToUpdate = soliToUpdate.filter(id__in=seleccion)     
                counts = soliToUpdate.count()                
                if accion == 'aceptar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[3][0])
                    messages.success(request, f'Se aceptaron las {counts} solicitudes seleccionadas con éxito')
                    solicitante_pk = None
                    modalidad_pk = None
                    for f in soliToUpdate.values():
                        solicitante_pk = f["solicitante_id"] 
                        modalidad_pk = f["modalidad_id"]
                        solicitante_inst = get_object_or_404(Solicitante, pk=solicitante_pk) 
                        modalidad_inst = get_object_or_404(Modalidad, pk=modalidad_pk)   
                        notif.nueva(solicitante_inst, f'Nos complace comunicarle que su solicitud para la modalidad de "{modalidad_inst.nombre}" ha sido ¡APROBADA!', 'solicitudes:historial')      
                elif accion == 'rechazar':
                    soliToUpdate.update(estado=Solicitud.ESTADO_CHOICES[4][0])
                    messages.success(request, f'Se rechazaron las {counts} solicitudes seleccionadas con éxito') 
                    for f in soliToUpdate.values():
                        solicitante_pk = f["solicitante_id"] 
                        modalidad_pk = f["modalidad_id"]
                        solicitante_inst = get_object_or_404(Solicitante, pk=solicitante_pk) 
                        modalidad_inst = get_object_or_404(Modalidad, pk=modalidad_pk)   
                        notif.nueva(solicitante_inst, f'Desafortunadamente su solicitud para la modalidad de "{modalidad_inst.nombre}" ha sido RECHAZADA.', 'solicitudes:historial')         
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

@login_required
def documentos_solicitante(request, pk):   
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    solicitante = get_object_or_404(Solicitante, pk=pk)  
    solicitud = get_object_or_404(Solicitud, solicitante=solicitante, ciclo=ciclo_actual())
    if notificar_si_falta_documentos(solicitud):
        messages.warning(request, 'Esta solicitud no tiene uno o varios archivos validos adjuntos, se notificó al solicitante que lo revise.')        
    modalidad = get_object_or_404(Modalidad, pk = solicitud.modalidad.pk)
    documentos = Documento.objects.filter(modalidad=solicitud.modalidad)
    listaDocumentos = []
    for documento in documentos:
        tupla = (documento, RespuestaDocumento.objects.filter(solicitud=solicitud, documento=documento).first())
        listaDocumentos.append(tupla)
    documentosResp = RespuestaDocumento.objects.filter(solicitud=solicitud)
    
    # print(documentos)
    # print(documentosResp)
    # print(solicitud.modalidad.pk)
    context = {
        'solicitud': solicitud,
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
        #print(f'{seleccionDenegados}')
        #print(f'{seleccionAceptados}')

        if seleccionAceptados:
            docsAceptadosToUpdate = documentosResp.filter(id__in = seleccionAceptados)   
            #print(docsAceptadosToUpdate)
            docsAceptadosToUpdate.update(estado=RespuestaDocumento.ESTADO_CHOICES[1][0])
        if seleccionDenegados:
            docsDenegadosToUpdate = documentosResp.filter(id__in = seleccionDenegados)   
            #print(docsDenegadosToUpdate)
            docsDenegadosToUpdate.update(estado=RespuestaDocumento.ESTADO_CHOICES[2][0]) 

        
        #Existieron documentos con error y otros fueron aprobados
        if seleccionDenegados != None :                                   
            #Si la cantidad de documentos recahzados es igual a la cantidad de los documentos totales de la modalidad
            #entonces se le manda al solicitante la notificación, de lo contrario no se manda nada
            if len(seleccionDenegados) == len(documentosResp):
                notif.nueva(solicitante, f'Todos sus documentos para la modalidad de "{modalidad.nombre}" han sido rechazados. Por favor verifíquelos y re súbalos.', 'solicitudes:documentos_convocatoria', urlArgs=[solicitud.modalidad_id]) 
            #Si hay algun elemento denegado entonces se notifica al usuario  
            else: 
                notif.nueva(solicitante, f'Algunos de sus documentos para la modalidad de "{modalidad.nombre}" han sido rechazados. Por favor, verifíquelos y re súbalos.', 'solicitudes:documentos_convocatoria', urlArgs=[solicitud.modalidad_id])           
            #No es necesario actualizar la info de la solicitud ya que las signals ligadas a los documentos respuesta
            #lo hacen automaticamente    
        #Todos los documentos fueron aceptados
        elif seleccionDenegados == None and seleccionAceptados != None:         
            #Si la cantidad de documentos aceptados es igual a la cantidad de los documentos totales de la modalidad
            #entonces se le manda al solicitante la notificación, de lo contrario no se manda nada
            if len(seleccionAceptados) == len(documentosResp):
            #No es necesario actualizar la info de la solicitud ya que las signals ligadas a los documentos respuesta
                notif.nueva(solicitante, f'Sus documentos para la modalidad de "{modalidad.nombre}" han sido aprobados.', 'solicitudes:historial')      

        if documentosResp.first():
            #el metodo .update()  en querysets no llama los recivers asi que se debe hacer almenos un save()
            documentosResp.first().save()
        
        messages.success(request, "Documentos de solicitud revisados con éxito.")
        return redirect(request.session['anterior'])
    return render(request, 'admin/documentosSolicitante.html', context)

@login_required
def concentradoSolicitud(request,pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    temp_dir =  os.path.join(settings.BASE_DIR,'temp/')     
    if not os.path.exists(temp_dir):# Si no existe, lo crea
        os.makedirs(temp_dir)

    uid = str(uuid.uuid4())
    uid = f'{uid}.zip'
    solicitud = get_object_or_404(Solicitud, pk=pk)
    documentosResp = RespuestaDocumento.objects.filter(solicitud=solicitud)    
    zip_filename = f'concentrado-{solicitud.solicitante.folio}-{solicitud.modalidad.nombre.replace(" ","_")}-{solicitud.modalidad.tipo}-{solicitud.ciclo}.zip'
    zip_filename = zip_filename.replace(' ','')
    with ZipFile(temp_dir + uid, 'w') as zipObj:
        for resp in documentosResp:
            originalName = os.path.basename(resp.file.name)
            extension = os.path.splitext(originalName)[1]
            filename = os.path.basename(resp.documento.nombre) + extension            
            zipObj.write(resp.file.path, arcname=filename)
    response = FileResponse(open(temp_dir+uid, 'rb'), as_attachment=True, filename=zip_filename)
    os.remove(temp_dir+uid) # Elimina el archivo temporal
    return response

@login_required
def concentradoConvocatoria(request,ciclo):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    temp_dir =  os.path.join(settings.BASE_DIR,'temp/')     
    if not os.path.exists(temp_dir):# Si no existe, lo crea
        os.makedirs(temp_dir)
        
    documentosResp = RespuestaDocumento.objects.filter(solicitud__ciclo=ciclo).select_related(
    'solicitud',
    'documento',
    'documento__modalidad',
    'solicitud__modalidad',
    'solicitud__solicitante',    
    )
    uid = str(uuid.uuid4())
    uid = f'{uid}.zip'
    zip_filename = f'CONCENTRADO-{ciclo}.zip'
    zip_filename = zip_filename.replace(' ','')

    xlPath = generarConcentradoXlsx(ciclo)

    with ZipFile(temp_dir + uid, 'w') as zipObj:
        zipObj.write(xlPath, arcname=(f'CONCENTRADO-{ciclo}.xlsx').replace(' ',''))

        total_solicitudes = len(documentosResp)
        for indice, resp in enumerate(documentosResp, start=1):
            print(f'generando concentrado docs: {(indice / total_solicitudes) * 100:.2f}%')        
            originalName = os.path.basename(resp.file.name)
            extension = os.path.splitext(originalName)[1]
            filename = os.path.basename(resp.documento.nombre) + extension    

            relative_path = os.path.join(
                f'{resp.solicitud.modalidad.nombre}-{resp.solicitud.modalidad.tipo}',
                resp.solicitud.solicitante.folio,
                filename
            )
            zipObj.write(resp.file.path, arcname=relative_path)

    response = FileResponse(open(temp_dir+uid, 'rb'), as_attachment=True, filename=zip_filename)
    os.remove(temp_dir+uid) # Elimina el archivo temporal
    os.remove(xlPath) # Elimina el archivo temporal
    return response

def generarConcentradoXlsx(ciclo):
    temp_dir =  os.path.join(settings.BASE_DIR,'temp/')     
    if not os.path.exists(temp_dir):# Si no existe, lo crea
        os.makedirs(temp_dir)
    uid = str(uuid.uuid4())
    uid = f'{uid}.xlsx'
    path = temp_dir + uid

    wb = Workbook()    
    ws = wb.active

    solicitudes = Solicitud.objects.filter(ciclo=ciclo).select_related(            
    'modalidad',
    'solicitante__municipio',    
    'solicitante__municipio__estado',
    'solicitante__carrera',
    'solicitante__carrera__institucion'
    )
    ws.append([
        'Estatus',
        'Estado_Beca',
        'Modalidad',
        'Folio',
        'Nombre',
        'Ap_Paterno',
        'Ap_Materno',
        'RFC',
        'Genero',
        'Punt_Genero',
        'Edad',
        'CURP',
        'Calle_y_Num',
        'CP',
        'Colonia',
        'Municipio',
        'Punt_Municipio',
        'Entidad_Federativa',
        'Tel_Casa',
        'Tel_Cel',
        'Correo',
        'Institución',
        'Punt_Institución',
        'Carrera',
        'Punt_Carrera',
        'Periodo',
        'Punt_Periodo',
        'Promedio',
        'Punt_Promedio',
        'Tipo_Solicitud',
        'Punt_Tipo_Solicitud',
        'Ingresos',
        'Punt_Ingresos',        
        'Total',
    ])
    seccionChoices = PuntajeGeneral.SECCION_CHOICES    
    puntajesGenero = PuntajeGeneral.objects.filter(tipo = seccionChoices[0][0])  
    puntajesPeriodo = PuntajeGeneral.objects.filter(tipo = seccionChoices[3][0])  
    puntajesPromedio = PuntajeGeneral.objects.filter(tipo = seccionChoices[4][0])     
    puntajeRenovacion = PuntajeGeneral.objects.get(tipo = seccionChoices[2][0], nombre='Renovación')                
    puntajeIngreso = PuntajeGeneral.objects.get(tipo = seccionChoices[2][0], nombre='Nuevo ingreso')                
    puntajesIngresosM = PuntajeGeneral.objects.filter(tipo = seccionChoices[1][0])
    q = Q(**{'nombre__icontains': 'Sueldo mensual familiar'}) 
    ingresoPreguntas = Elemento.objects.filter(tipo=Elemento.TIPO_CHOICES[1][0]).filter(q)   
    ids_preguntas = ingresoPreguntas.values_list('id', flat=True)

    total_solicitudes = len(solicitudes)
    for indice, solicitud in enumerate(solicitudes, start=1):
        print(f'generando concentrado xlsx: {(indice / total_solicitudes) * 100:.2f}%')
        values = []
        nuevoPuntaje = 0
        #Estatus
        try:
            documentos_modalidad = solicitud.modalidad.documento_set.all()
            respuestas_documentos_solicitud = RespuestaDocumento.objects.filter(solicitud=solicitud) 
            if set(documentos_modalidad) == set({resp.documento for resp in respuestas_documentos_solicitud}):        
                values.append('Completo')
            else:
                values.append('Incompleto')
        except Exception as e:
            values.append(None)

        #Estado_Beca
        try:
            values.append(solicitud.estado)
        except Exception as e:
            values.append(None)

        #Modalidad
        try:
            values.append(solicitud.modalidad.nombre)
        except Exception as e:
            values.append(None)

        #Folio
        try:
            values.append(solicitud.solicitante.folio)
        except Exception as e:
            values.append(None)

        #Nombre
        try:
            values.append(solicitud.solicitante.nombre)
        except Exception as e:
            values.append(None)

        #Ap_Paterno
        try:
            values.append(solicitud.solicitante.ap_paterno)
        except Exception as e:
            values.append(None)

        #Ap_Materno
        try:
            values.append(solicitud.solicitante.ap_materno)
        except Exception as e:
            values.append(None)

        #rfc
        try:
            values.append(solicitud.solicitante.rfc)
        except Exception as e:
            values.append(None)

        #genero
        try:
            values.append(solicitud.solicitante.genero)
        except Exception as e:
            values.append(None)

        #Punt_genero
        try:            
            for puntaje in puntajesGenero:
                if solicitud.solicitante.genero == puntaje.nombre:
                    nuevoPuntaje += puntaje.puntos
                    values.append(puntaje.puntos)
                    break
                elif puntaje.id == puntajesGenero.last().id:
                    values.append(None)
        except Exception as e:
            values.append(None)

        #Edad
        try:
            hoy = date.today()
            fecha_nacimiento = solicitud.solicitante.fecha_nacimiento            
            edad = round((hoy - fecha_nacimiento).days / 365.25)
            values.append(edad)
        except Exception as e:
            values.append(None)

        #CURP
        try:
            values.append(solicitud.solicitante.curp)
        except Exception as e:
            values.append(None)

        #Calle_y_Num
        try:
            values.append(f'{solicitud.solicitante.calle} {solicitud.solicitante.numero}')
        except Exception as e:
            values.append(None)

        #CP
        try:
            values.append(solicitud.solicitante.codigo_postal)
        except Exception as e:
            values.append(None)
        #Colonia
        try:
            values.append(solicitud.solicitante.colonia)
        except Exception as e:
            values.append(None)

        #Municipio
        try:
            values.append(solicitud.solicitante.municipio.nombre)
        except Exception as e:
            values.append(None)

        #Punt_Municipio
        try:
            puntajeMun = PuntajeMunicipio.objects.get(municipio=solicitud.solicitante.municipio_id)
            nuevoPuntaje += puntajeMun.puntos
            values.append(puntajeMun.puntos)
        except PuntajeMunicipio.DoesNotExist:
            values.append(0)
        except Exception as e:
            values.append(None)

        #Entidad_Federativa
        try:
            values.append(solicitud.solicitante.municipio.estado.nombre)
        except Exception as e:
            values.append(None)

        #Tel_Casa
        try:
            values.append(solicitud.solicitante.tel_fijo)
        except Exception as e:
            values.append(None)

        #Tel_Cel
        try:
            values.append(solicitud.solicitante.tel_cel)
        except Exception as e:
            values.append(None)

        #Correo
        try:
            values.append(solicitud.solicitante.email)
        except Exception as e:
            values.append(None)

        #Institución
        try:
            values.append(solicitud.solicitante.carrera.institucion.nombre)
        except Exception as e:
            values.append(None)

        #Punt_Institución
        try:
            puntos = solicitud.solicitante.carrera.institucion.puntos
            nuevoPuntaje += puntos
            values.append(puntos)
        except Exception as e:
            values.append(None)

        #Carrera
        try:
            values.append(solicitud.solicitante.carrera.nombre)
        except Exception as e:
            values.append(None)

        #Punt_Carrera
        try:
            carrera = solicitud.solicitante.carrera
            nuevoPuntaje += carrera.puntos
            values.append(carrera.puntos)
        except Exception as e:
            values.append(None)

        #Periodo
        try:            
            values.append(solicitud.solicitante.grado)
        except Exception as e:
            values.append(None)

        #Punt_Periodo
        try:
            for puntaje in puntajesPeriodo:
                limite_inferior, limite_superior = map(int, puntaje.nombre.split('-'))
                if limite_inferior <= int(solicitud.solicitante.grado) <= limite_superior:
                    nuevoPuntaje += puntaje.puntos
                    values.append(puntaje.puntos)
                    break
                elif puntaje.id == puntajesPeriodo.last().id:
                    values.append(None)
        except Exception as e:
            values.append(None)

        #Promedio
        try:
            values.append(solicitud.solicitante.promedio)
        except Exception as e:
            values.append(None)

        #Punt_Promedio
        try:               
            for puntaje in puntajesPromedio:
                limite_inferior, limite_superior = map(float, puntaje.nombre.split('-'))            
                if limite_inferior <= solicitud.solicitante.promedio <= limite_superior:
                    nuevoPuntaje += puntaje.puntos
                    values.append(puntaje.puntos)
                    break
                elif puntaje.id == puntajesPromedio.last().id:
                    values.append(0)
        except Exception as e:
            values.append(None)

        #Tipo_Solicitud
        try:
            values.append(solicitud.tipo)
        except Exception as e:
            values.append(None)

        #Punt_Tipo_Solicitud
        try:
            if solicitud.solicitante.es_renovacion:                
                nuevoPuntaje += puntajeRenovacion.puntos
                values.append(puntajeRenovacion.puntos)
            else:                
                nuevoPuntaje += puntajeIngreso.puntos
                values.append(puntajeIngreso.puntos)
        except Exception as e:
            values.append(None)        

        #Ingresos
        #Punt_Ingresos
        try:            
            ingresos = [] #lista de querysets relacionados con ingresos    
            # Obtener todas las respuestas que pertenecen a las preguntas
            respuestas = RNumerico.objects.filter(elemento__id__in=ids_preguntas, solicitante=solicitud.solicitante)
            ingresos = respuestas.values_list('valor', flat=True)
            ingresos = list(map(int, ingresos))        
            ingresoTotal = sum(ingresos)   
            values.append(ingresoTotal)
            for puntaje in puntajesIngresosM:
                limite_inferior, limite_superior = map(int, puntaje.nombre.replace('$', '').split('-'))
                if limite_inferior <= ingresoTotal <= limite_superior:
                    nuevoPuntaje += puntaje.puntos
                    values.append(puntaje.puntos)
                    break
                elif puntaje.id == puntajesIngresosM.last().id:
                    values.append(None)
        except Exception as e:
            values.append(None)        

        #Total
        try:
            values.append(nuevoPuntaje)
        except Exception as e:
            values.append(None)

        #print(values)
        ws.append(values)

    wb.save(path)
    return path
