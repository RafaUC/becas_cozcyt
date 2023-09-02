from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms as FForms
from usuarios.views import verificarRedirect
from usuarios.models import Usuario, Solicitante
from .models import Seccion, Elemento, Opcion, Respuesta
from .forms import RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm

# Create your views here.

@login_required
def estudioSE(request):    
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE
    preguntasEstudio = Seccion.objects.prefetch_related('elemento_set__opcion_set').all()
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses()
    for respuesta in respuestasExistentes:
        respuestas[respuesta.elemento_id] = respuesta

    #generando Forms
    #se genera un diccionario con los tipos de forms
    formModels = {}
    formModelsConOpcion = [ROpcionMultipleForm, RCasillasForm, RDesplegableForm]     
    for formtype in [RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm]:
        formModels[formtype.Meta.model] = formtype    
    
    if request.method == 'GET':  
        for seccion in preguntasEstudio:    
            for elemento in seccion.elemento_set.all():            
                #si la pregunta no es de una opcion de las que se tiene formulario se salta esta iteracion
                if elemento.getRespuestaModel() is None:
                    continue
                formModel = formModels[elemento.getRespuestaModel()]
                #si ya existe una respuesta de esta pregunta
                if elemento.id in respuestas:                
                    forms[elemento.id] = formModel(instance=respuestas[elemento.id], prefix=f'respuesta_{elemento.id}')
                #si no existe una respuesta de esta pregunta    
                else:                
                    forms[elemento.id] = formModel(elemento=elemento, solicitante=solicitante, prefix=f'respuesta_{elemento.id}')
                #si son formularios de opcion se asignan las opciones
                if formModel in formModelsConOpcion:
                    choices = [(opcion.id, opcion.nombre) for opcion in elemento.opcion_set.all()]                
                    if isinstance(forms[elemento.id].fields['respuesta'].widget, FForms.Select):
                        # Agrega la opción en blanco al comienzo solo si el campo es un 'select'
                        choices.insert(0, ("", "---------"))  
                    if elemento.opcionOtro :
                        choices.append((opcOtro.id, opcOtro.nombre) )
                    forms[elemento.id].fields['respuesta'].choices = choices
                    #forms[elemento.id].fields['respuesta'].queryset = elemento.opcion_set.all()
    
    if request.method == 'POST':  
        print(request.POST)
        for seccion in preguntasEstudio:    
            for elemento in seccion.elemento_set.all():            
                #si la pregunta no es de una opcion de las que se tiene formulario se salta esta iteracion
                if elemento.getRespuestaModel() is None:
                    continue
                formModel = formModels[elemento.getRespuestaModel()]
                #si ya existe una respuesta de esta pregunta
                if elemento.id in respuestas:                
                    forms[elemento.id] = formModel(request.POST, instance=respuestas[elemento.id], prefix=f'respuesta_{elemento.id}')
                #si no existe una respuesta de esta pregunta    
                else:                
                    forms[elemento.id] = formModel(request.POST, elemento=elemento, solicitante=solicitante, prefix=f'respuesta_{elemento.id}')
                #si son formularios de opcion se asignan las opciones
                if formModel in formModelsConOpcion:
                    choices = [(opcion.id, opcion.nombre) for opcion in elemento.opcion_set.all()]                
                    if isinstance(forms[elemento.id].fields['respuesta'].widget, FForms.Select):
                        # Agrega la opción en blanco al comienzo solo si el campo es un 'select'
                        choices.insert(0, ("", "---------"))  
                    if elemento.opcionOtro :
                        choices.append((opcOtro.id, opcOtro.nombre) )
                    forms[elemento.id].fields['respuesta'].choices = choices
                    #forms[elemento.id].fields['respuesta'].queryset = elemento.opcion_set.all()

        for form in forms.values():
            form.is_valid()
            print(form.instance.elemento_id)
            print(form.errors)
        print('aa')

            

    context = {            
            'forms': forms,            
            'preguntasEstudio': preguntasEstudio,   
        }


    return render(request, 'solicitante/estudioSE.html', context)