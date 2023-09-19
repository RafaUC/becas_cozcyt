from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms as FForms
from django.db.models import Prefetch
from usuarios.views import verificarRedirect
from usuarios.models import Usuario, Solicitante
from .models import Seccion, Elemento, Opcion, Respuesta, RAgregacion
from .forms import RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm

import os
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
import logging


#logica para crear las instancias de las forms
def crearForms(forms, opcOtro, requestPost, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante):
    for seccion in preguntasEstudio:    
            for elemento in seccion.elemento_set.all():            
                #si la pregunta no es de una opcion de las que se tiene formulario se salta esta iteracion
                if elemento.getRespuestaModel() is None:
                    continue
                formModel = formModels[elemento.getRespuestaModel()]
                esTipoUnico = seccion.tipo == Seccion.TIPOS_CHOICES[0][0]                
                #si ya existe una respuesta de esta pregunta
                if (esTipoUnico and elemento.id in respuestas) and isinstance(respuestas[elemento.id], formModel.Meta.model):                
                    forms[elemento.id] = formModel(requestPost, instance=respuestas[elemento.id], prefix=f'respuesta_{elemento.id}')
                #si no existe una respuesta de esta pregunta    
                else:     
                    #si existe una respuesta pero no coincide con el modelo de la pregunta esta se elimina para crear una nueva
                    if (esTipoUnico and elemento.id in respuestas):
                        respuestas[elemento.id].delete()           
                    forms[elemento.id] = formModel(requestPost, elemento=elemento, solicitante=solicitante, prefix=f'respuesta_{elemento.id}')
                #si son formularios de opcion se asignan las opciones
                if formModel in formModelsConOpcion:
                    choices = [(opcion.id, opcion.nombre) for opcion in elemento.opcion_set.all()]                
                    if isinstance(forms[elemento.id].fields['respuesta'].widget, FForms.Select):
                        # Agrega la opción en blanco al comienzo solo si el campo es un 'select'
                        choices.insert(0, ("", "---------"))  
                    if elemento.opcionOtro :
                        choices.append((opcOtro.id, opcOtro.nombre) )
                    forms[elemento.id].fields['respuesta'].choices = choices

@login_required
def estudioSE(request):    
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.all().prefetch_related('elemento_set__opcion_set')    
    descargarPDF = False
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses().select_related('elemento__seccion')
    for respuesta in respuestasExistentes:        
        respuestas[respuesta.elemento_id] = respuesta
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)    

    '''        
    for clave, lista in registrosA.items():
        print(f"Clave: {clave}")
        print("Elementos de la lista:")
        for elemento in lista:
            print(elemento)
        print()  #'''

    #generando Forms
    #se genera un diccionario con los tipos de forms
    formModels = {}
    formModelsConOpcion = [ROpcionMultipleForm, RCasillasForm, RDesplegableForm]     
    for formtype in [RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm]:
        formModels[formtype.Meta.model] = formtype    
    
    if request.method == 'GET':  
        crearForms(forms, opcOtro, None, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)
                    
    
    if request.method == 'POST':          
        crearForms(forms, opcOtro, request.POST, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)
                    
        
        #Solo se validan y guardan las respuestas de secciones de tipo 'unico', las de 'agregacion' se omiten
        todoValido = True
        for form in forms.values():
            tipo = form.instance.elemento.seccion.tipo
            if tipo == Seccion.TIPOS_CHOICES[0][0]:
                if not form.is_valid():
                    todoValido = False
            elif tipo == Seccion.TIPOS_CHOICES[1][0]:
                form.errors.clear()                                
        
        if todoValido:
            for form in forms.values():
                if form.instance.elemento.seccion.tipo == Seccion.TIPOS_CHOICES[0][0]:
                    form.save() 
            messages.success(request, 'Estudio Socioeconómico guardado con éxito')
            #return redirect('estudioSE:estudioSE_PDF')  
            descargarPDF = True
        else:            
            for i, seccion in enumerate(preguntasEstudio):                           
                for j, elemento in enumerate(seccion.elemento_set.all()):                  
                    if elemento.id in forms and forms[elemento.id].errors:   
                        for error in forms[elemento.id].errors.values():                                             
                            messages.error(request, [f'Seccion {seccion.nombre}: Pregunta {elemento.nombre}', error])                    
            messages.warning(request, 'No se pudieron guardar los cambios: Formularios no validos')            
            

    context = {      
            'opcOtro': opcOtro,
            'forms': forms,            
            'preguntasEstudio': preguntasEstudio,   
            'registrosA': registrosA,
            'descargarPDF': descargarPDF,
        }


    return render(request, 'solicitante/estudioSE.html', context)



@login_required
def agregarR(request, seccionID):
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.filter(id = seccionID).prefetch_related('elemento_set__opcion_set')    
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}    
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante, respuesta__elemento__seccion_id=seccionID)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)        

    #generando Forms
    #se genera un diccionario con los tipos de forms
    formModels = {}
    formModelsConOpcion = [ROpcionMultipleForm, RCasillasForm, RDesplegableForm]     
    for formtype in [RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm]:
        formModels[formtype.Meta.model] = formtype    
        
    if request.method == 'GET':  
        crearForms(forms, opcOtro, None, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)                        

    if request.method == 'POST':          
        crearForms(forms, opcOtro, request.POST, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)
                    
        
        #Solo se validan y guardan las respuestas de secciones de tipo 'unico', las de 'agregacion' se omiten
        todoValido = True
        for form in forms.values():            
            if not form.is_valid():
                todoValido = False                                        
        
        if todoValido:
            rAgregacionInstance = RAgregacion.objects.create()
            for form in forms.values():     
                form.instance.rAgregacion = rAgregacionInstance
                form.save()                 
            messages.success(request, 'Registro agregado con éxito')
            return redirect('estudioSE:AgregarR', seccionID)  
        else:            
            for i, seccion in enumerate(preguntasEstudio):                           
                for j, elemento in enumerate(seccion.elemento_set.all()):                  
                    if elemento.id in forms and forms[elemento.id].errors:   
                        for error in forms[elemento.id].errors.values():                                             
                            messages.error(request, [f'Seccion {seccion.nombre}: Pregunta {elemento.nombre}', error])                    
            messages.warning(request, 'No se pudo guardar el registro: Formularios no validos')
            

    context = {     
            'mensajes' : 'mensajes.html',
            'opcOtro': opcOtro,
            'forms': forms,            
            'preguntasEstudio': preguntasEstudio,   
            'registrosA': registrosA,
        }


    return render(request, 'solicitante/formularioBase.html', context)



@login_required
def eliminarR(request, seccionID, registroID):
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    registroAgregacion = get_object_or_404(RAgregacion, pk=registroID)      
    respuestas = Respuesta.objects.filter(rAgregacion=registroAgregacion, solicitante=solicitante).select_subclasses()
    
    if respuestas.exists() and respuestas.first().elemento.seccion_id == seccionID:
        print(f'eliminando {seccionID} - {registroID} - {respuestas.first().getStringValue()}')
        registroAgregacion.delete()
        messages.success(request, 'Registro eliminado con exito')
        return redirect('estudioSE:AgregarR', seccionID)  
    else:
        messages.error(request, 'No se pudo eliminar el Registro')




@login_required
def getEstudioPDF(request):        
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)

    ###########OBtener informacion ###############
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.all().prefetch_related('elemento_set__opcion_set')    
    descargarPDF = False
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses().select_related('elemento__seccion')
    for respuesta in respuestasExistentes:        
        respuestas[respuesta.elemento_id] = respuesta    
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)    

    valoresRespuesta = {} #contiene los valores de las respuestas, una lista de strings si son opciones y una lista anidada en esa lista por las opciones seleccionadas
    for seccion in preguntasEstudio:
        for elemento in seccion.elemento_set.all():
            if any(elemento.tipo == choice[0] for choice in Elemento.TIPO_CHOICES[6:]):
                if elemento.tipo == 'casillas':
                    fAClasses = ['fa fa-square-o','fa fa-check-square']
                else:
                    fAClasses = ['fa fa-circle-thin', 'fa fa-check-circle']
                choices = [fAClasses]
                if respuestas[elemento.id].respuesta and not isinstance(respuestas[elemento.id].respuesta, Opcion):
                    multiples = respuestas[elemento.id].respuesta.all()                    
                else :
                    multiples = None
                #if opcion.id in respuestas[elemento.id].respuesta:
                for opcion in elemento.opcion_set.all():                    
                        
                    if (multiples and opcion in multiples) or (not multiples and opcion.id == respuestas[elemento.id].respuesta_id):
                        if opcion.nombre == 'Otro' :
                            choices.append([opcion.nombre, respuestas[elemento.id].otro])
                        else:
                            choices.append([opcion.nombre])
                    else:
                        choices.append(opcion.nombre)
                valoresRespuesta[elemento.id] = choices
            elif elemento.tipo == Elemento.TIPO_CHOICES[0][0]:
                pass
            else:
                valoresRespuesta[elemento.id] = respuestas[elemento.id].getStringValue()

    template = get_template('solicitante/pdfTemplate.html')
    context = {               
            'solicitante': solicitante,
            'opcOtro': opcOtro,
            'valoresRespuesta': valoresRespuesta,            
            'preguntasEstudio': preguntasEstudio,   
            'registrosA': registrosA,
            'descargarPDF': descargarPDF,
        }

    #logger = logging.getLogger('weasyprint')
    #logger.addHandler(logging.FileHandler('./weasyprint.log'))

    # Renderiza el template con los datos
    #return render(request, 'solicitante/pdfTemplate.html', context)
    html_content = template.render(context)

    #css_bootstrap_grid = os.path.join(settings.BASE_DIR, "static/css/bootstrap-grid.css")    
    #css_main = os.path.join(settings.BASE_DIR, "static/css/main.css")       
    # Crea un objeto HTML a partir del contenido HTML
    html = HTML(string=html_content, base_url=request.build_absolute_uri())    
    # Genera el PDF
    #pdf_file = html.write_pdf(stylesheets=[CSS(css_bootstrap_grid), CSS(css_main)])    
    pdf_file = html.write_pdf()    
    # Devuelve el PDF como una respuesta HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="EstudioSocioeconomico.pdf"'  # Cambia 'inline' a 'attachment'
    #response['Content-Disposition'] = 'inline; filename="EstudioSocioeconomico.pdf"'
    return response