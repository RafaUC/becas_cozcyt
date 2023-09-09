from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms as FForms
from django.db.models import Prefetch
from usuarios.views import verificarRedirect
from usuarios.models import Usuario, Solicitante
from .models import Seccion, Elemento, Opcion, Respuesta, RAgregacion
from .forms import RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm

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
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses().select_related('elemento')
    for respuesta in respuestasExistentes:        
        respuestas[respuesta.elemento_id] = respuesta
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        sID = respuesta.elemento.seccion_id
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
                    

        todoValido = True
        for form in forms.values():
            if not form.is_valid():
                todoValido = False
        
        if todoValido:
            for form in forms.values():
                form.save() 
            messages.success(request, 'Estudio Socioeconómico guardado con éxito')
            #return redirect(settings.LOGIN_REDIRECT_URL)     
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
        }


    return render(request, 'solicitante/estudioSE.html', context)