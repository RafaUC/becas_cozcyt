from django.shortcuts import get_object_or_404, redirect, render
from usuarios.views import verificarRedirect
from usuarios.models import Usuario
from .models import Seccion, Elemento, Opcion
from.forms import SeccionFormSet, ElementoFormSet

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
    for seccion in secciones:
        dictElemForm[str(seccion.id)] = ElementoFormSet(instance=seccion, prefix='elemento_formset_%s' % seccion.id)

    if request.method == 'POST':                       
        seccionFormset = SeccionFormSet(request.POST, prefix='seccion_formset')                        

        if seccionFormset.is_valid(): # and elementoFormset.is_valid():
            todoValido = True                                
            dictElemForm = {}
            seccionFormset.save()
            for seccion in seccionFormset.forms:                            
                seccionInstancia = seccion.instance
                elementoFormset = ElementoFormSet(request.POST, prefix='elemento_formset_%s' % seccionInstancia.id, instance=seccionInstancia)                                     

                elementoFormset.is_valid()
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

                dictElemForm[str(seccionInstancia.id)] = elementoFormset                
                if elementoFormset.is_valid():                                  
                    elementoFormset.save()  
                    pass   
                else:   
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
    }
    
    

    return render(request, 'admin/config_estudioSE.html', context)
        