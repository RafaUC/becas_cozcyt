from django.shortcuts import get_object_or_404, redirect, render
from usuarios.views import verificarRedirect
from usuarios.models import Usuario
from .models import Seccion, Elemento, Opcion
from.forms import SeccionFormSet, ElementoFormSet, OpcionFormSet

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
        seccionFormset = SeccionFormSet(request.POST, prefix='seccion_formset')  
        seccionFormset.is_valid()
        
        non_empty_forms = []
        empty_forms = []
        for form in seccionFormset.forms:                    
            if form.cleaned_data:
                non_empty_forms.append(form)
            else:
                empty_forms.append(form)
        # Unir ambas listas para tener los formularios no vacíos al principio y los vacíos al final
        ordered_forms = non_empty_forms + empty_forms                
        # Actualizar el formset con la nueva lista de formularios
        seccionFormset.forms = ordered_forms                        

        seccionFormset.is_valid()
        for seccion in seccionFormset:
            print(seccion.cleaned_data)

        if seccionFormset.is_valid(): # and elementoFormset.is_valid():
            print('secciones es valida')
            todoValido = True                                
        dictElemForm = {}
        dictOpcionForm = {}
        
        for seccion in seccionFormset.forms: 
            seccionInstancia = seccion.instance
            print(seccion.cleaned_data)    

            if (seccion.cleaned_data and seccion.cleaned_data['DELETE']):
                if seccionInstancia.id is not None:
                    seccionInstancia.delete()
            else :
                
                print('dentro de seccion : ')                                       
                print(seccion.cleaned_data)                    
                seccionFormsetId = (seccion.prefix.split('-').pop())
                elementoFormset = ElementoFormSet(request.POST, prefix='elemento_formset-%s' % seccionFormsetId, instance=seccionInstancia)                                                     
                elementoFormset.is_valid()
                
                for elemento in elementoFormset:
                    print(elemento.cleaned_data)

                non_empty_forms = []
                empty_forms = []
                for form in elementoFormset.forms:                    
                    if form.cleaned_data:
                        non_empty_forms.append(form)
                    else:
                        empty_forms.append(form)
                # Unir ambas listas para tener los formularios no vacíos al principio y los vacíos al final
                ordered_forms = non_empty_forms + empty_forms                
                # Actualizar el formset con la nueva lista de formularios
                elementoFormset.forms = ordered_forms               
                dictElemForm[seccion.prefix] = elementoFormset    

                if elementoFormset.is_valid() and seccion.is_valid(): 
                    if (seccion.cleaned_data ): #La seccion no esta en blanco
                        seccion.save()
                    print('elementos es valida')                                       
                else:   
                    print('elemntos no valido')
                    print(elementoFormset.errors)
                    todoValido = False  
                
                
                for elemento in elementoFormset.forms: 
                    elementoInstancia = elemento.instance
                    print(elemento.cleaned_data)                        

                    if (elemento.cleaned_data and elemento.cleaned_data['DELETE']):
                        if elementoInstancia.id is not None:
                            elementoInstancia.delete()
                    else :
                        print('dentro de elemento : ')   
                        print(elemento.cleaned_data)    
                        elemFormsetId = elemento.prefix.split('-') 
                        newId = elemFormsetId[1] + '-' + elemFormsetId[2]                    
                        opcionFormset = OpcionFormSet(request.POST, instance=elementoInstancia, prefix='opcion_formset-%s' % newId)     
                        opcionFormset.is_valid()

                        for opcion in opcionFormset:
                            print(opcion.cleaned_data)

                        non_empty_forms = []
                        empty_forms = []
                        for form in opcionFormset.forms:                    
                            if form.cleaned_data:
                                non_empty_forms.append(form)
                            else:
                                empty_forms.append(form)
                        # Unir ambas listas para tener los formularios no vacíos al principio y los vacíos al final
                        ordered_forms = non_empty_forms + empty_forms                
                        # Actualizar el formset con la nueva lista de formularios
                        opcionFormset.forms = ordered_forms               
                        dictOpcionForm[elemento.prefix] = opcionFormset    

                        if opcionFormset.is_valid() and elemento.is_valid(): 
                            if (elemento.cleaned_data ):
                                print('elementos es valida')     
                                elemento.save()   
                                opcionFormset.save()                                  
                        else:   
                            print('opciones no valido')
                            print(opcionFormset.errors)
                            todoValido = False  
                            

                
        
        print("todo valido: ")
        print(todoValido)

        if todoValido:                
            return redirect('estudioSE:AConfigEstudio')  
        else:
            print('seccion no valid')
            print(seccionFormset.errors)
            
        

    context = {
        'seccionFormset': seccionFormset,
        'dictElemForm': dictElemForm,
        'dictOpcionForm': dictOpcionForm,
    }
    
    

    return render(request, 'admin/config_estudioSE.html', context)
        