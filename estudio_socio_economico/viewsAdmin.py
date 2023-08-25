from django.shortcuts import get_object_or_404, redirect, render
from usuarios.views import verificarRedirect
from usuarios.models import Usuario
from .models import Seccion, Elemento, Opcion
from.forms import SeccionFormSet, ElementoFormSet, OpcionFormSet
from django.contrib import messages
# Create your views here.

# Crear el inline formset para Elemento    
# Donde "ElementoForm" es el ModelForm personalizado para el modelo Elemento que definiste anteriormente.
def configEstudio(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)  
      
    secciones = Seccion.objects.all()
    seccionFormset = SeccionFormSet(queryset=secciones, prefix='seccion_formset')        
    dictElemForm = {}
    dictOpcionForm = {}
    for seccionform in seccionFormset:
        seccionInstancia = seccionform.instance        
        seccionFormsetId = (seccionform.prefix.split('-').pop())         
        dictElemForm[seccionform.prefix] = ElementoFormSet(instance=seccionInstancia, prefix='elemento_formset-%s' % seccionFormsetId)
        for elementoform in dictElemForm[seccionform.prefix]:
            elemInstancia = elementoform.instance
            elemFormsetId = elementoform.prefix.split('-') 
            newId = elemFormsetId[1] + '-' + elemFormsetId[2]                    
            dictOpcionForm[elementoform.prefix] = OpcionFormSet(instance=elemInstancia, prefix='opcion_formset-%s' % newId)                                           


    if request.method == 'POST':  
        todoValido = True  
        dictElemForm = {}   #diccionario que contiene todos los formset de elementos
        dictOpcionForm = {}   #diccionario que contiene todos los formset de objetos             
        
        #obtenemos los formset de secciones, elementos y opciones y hacemos todas las validaciones
        seccionFormset = SeccionFormSet(request.POST, prefix='seccion_formset')  
        if not seccionFormset.is_valid():
            todoValido = False
        for seccion in seccionFormset.forms:
            seccionInstancia = seccion.instance     
            seccionFormsetId = (seccion.prefix.split('-').pop())
            elementoFormset = ElementoFormSet(request.POST, instance=seccionInstancia, prefix='elemento_formset-%s' % seccionFormsetId)                                                     
            if not elementoFormset.is_valid(): #generamos el cleaned data
                todoValido = False
            dictElemForm[seccion.prefix] = elementoFormset    

            #obtenemos el opcionformset  de cada elemento
            for elemento in elementoFormset.forms: 
                elemInstancia = elemento.instance
                elemFormsetId = elemento.prefix.split('-') 
                newId = elemFormsetId[1] + '-' + elemFormsetId[2]                    
                opcionFormset = OpcionFormSet(request.POST, instance=elemInstancia, prefix='opcion_formset-%s' % newId)     
                if not opcionFormset.is_valid(): #generamos el cleaned data
                    todoValido = False
                dictOpcionForm[elemento.prefix] = opcionFormset   #añadimos el opcionFormset a el diccionario de opcionesformset

                #verificamos que un formulario vacio no tenga formularios dependientes de el con datos
                #si es asi, no es valido, y agregamos los errores manualmente
                if (elemento.cleaned_data and not seccion.cleaned_data and not elemento.cleaned_data['DELETE']):
                    todoValido = False  
                    seccion.cleaned_data['error'] = 'Los campos de la sección son obligatorios'
                    seccion.add_error(None, seccion.cleaned_data['error'])
                for opcionForm in opcionFormset:
                    if (opcionForm.cleaned_data and not elemento.cleaned_data and not opcionForm.cleaned_data['DELETE']):
                        todoValido = False  
                        elemento.cleaned_data['error'] = 'Los campos de la pregunta son obligatorios'
                        elemento.add_error(None, elemento.cleaned_data['error'])
                    if (opcionForm.cleaned_data and not seccion.cleaned_data and not opcionForm.cleaned_data['DELETE']):
                        todoValido = False              
                        seccion.cleaned_data['error'] = 'Los campos de la sección son obligatorios'
                        seccion.add_error(None, seccion.cleaned_data['error'])
        
        #los formularios de los formset se reordenan para que el formulario extra default quede ultimo        
        non_empty_forms = []
        empty_forms = []
        for form in seccionFormset.forms:                    
            if form.cleaned_data:
                non_empty_forms.append(form)
            else:
                form.childAsinfo = 'on'
                empty_forms.append(form)        
        ordered_forms = non_empty_forms + empty_forms                        
        seccionFormset.forms = ordered_forms     
                   
        for elementoFormset in dictElemForm.values():             
           
            non_empty_forms = []
            empty_forms = []
            for form in elementoFormset.forms:                    
                if form.cleaned_data:
                    non_empty_forms.append(form)
                else:
                    empty_forms.append(form)            
            ordered_forms = non_empty_forms + empty_forms                            
            elementoFormset.forms = ordered_forms    

        for opcionFormset in dictOpcionForm.values():           
                    
            non_empty_forms = []
            empty_forms = []
            for form in opcionFormset.forms:                    
                if form.cleaned_data:
                    non_empty_forms.append(form)
                else:
                    empty_forms.append(form)            
            ordered_forms = non_empty_forms + empty_forms                            
            opcionFormset.forms = ordered_forms                                                                       

        #imprimir datos para debug 
        '''
        print('\n\n\n\n\nInicio Debug')
        for seccion in seccionFormset:
            print('\n-----seccion '+seccion.prefix+' -----')
            print(seccion.cleaned_data)
            for elemento in dictElemForm[seccion.prefix]:
                print('\n'+elemento.prefix)
                print(elemento.cleaned_data)
                for opcion in dictOpcionForm[elemento.prefix]:
                    print(opcion.prefix)
                    print(opcion.cleaned_data) #'''

        if todoValido: 
            #'''    
            print('=============== Todo es valido ===============\n') #'''
            seccionFormset.save()           
            for elemFormset in dictElemForm.values():                
                if elemFormset.instance.id is not None:
                    elemFormset.save()
            for OpcionFormset in dictOpcionForm.values():
                if OpcionFormset.instance.id is not None:
                    OpcionFormset.save()
            messages.success(request, 'Cambios guardados con éxito')
            return redirect('estudioSE:AConfigEstudio')              
        else:
            #generamos mensajes de error
            messages.warning(request, 'No se pudieron guardar los cambios: Formularios no validos')
            for i, seccion in enumerate(seccionFormset):            
                if seccion.errors:                    
                    messages.error(request, [f'Seccion {i+1}', seccion.errors])
                for j, elemento in enumerate(dictElemForm[seccion.prefix]):                  
                    if elemento.errors:                    
                        messages.error(request, [f'Seccion {i+1}: Elmento {j+1}', elemento.errors])
                    for k, opcion in enumerate(dictOpcionForm[elemento.prefix]):
                        if opcion.errors:                    
                            messages.error(request, [f'Seccion {i+1}: Elmento {j+1}: Opcion {k+1}', opcion.errors]) #'''

            #imprimir datos error pra debug
            '''
            print('\n--------------- Todo no valido ---------------\n')     
            print(seccionFormset.prefix)
            print(seccionFormset.errors)
            for elemFormset in dictElemForm.values():                                
                print(elemFormset.prefix)
                print(elemFormset.errors)
            for OpcionFormset in dictOpcionForm.values():      
                print(OpcionFormset.prefix)          
                print(OpcionFormset.errors) #'''
            print('--------------- Error Invalido ---------------\n')     
            
        

    context = {
        'seccionFormset': seccionFormset,
        'dictElemForm': dictElemForm,
        'dictOpcionForm': dictOpcionForm,
    }
    
    

    return render(request, 'admin/config_estudioSE.html', context)
        