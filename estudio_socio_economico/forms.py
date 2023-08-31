from django import forms
from .models import Seccion, Opcion, Elemento
from django.forms import inlineformset_factory, modelformset_factory
from .models import RNumerico, RTextoCorto, RTextoParrafo, RHora, RFecha, ROpcionMultiple, RCasillas, RDesplegable



class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'tipo', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-lg font-semi-bold border-3'}),
            'tipo': forms.RadioSelect(attrs={'class': 'ms-3'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'type': 'hidden'}),
        }
        labels = {
            'nombre': 'Nombre de la Sección',
            'tipo': 'Tipo de la Sección',
            'orden': 'orden',
        }
        
        

class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ['elemento', 'nombre', 'orden']
        widgets = {
            'elemento': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'opcion-text form-control border-3 p-0 m-0', 'onkeyup': 'updateOpcionInputSize(this)', 'onkeydown': 'updateOpcionInputSize(this)'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'type': 'hidden'}),
        }
        labels = {
            'elemento': 'Elemento',
            'nombre': 'Nombre Opción',
            'orden': 'orden',
        }
        
        

class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = ['seccion', 'nombre', 'obligatorio', 'opcionOtro', 'numMin', 'numMax', 'row', 'col', 'tipo',]
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-control form-control-sm border-3', 'placeholder': 'Selecciona una sección'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm font-semi-bold border-3 ', 'placeholder': 'Nombre de la pregunta'}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'checkbox-principal form-check-input'}),            
            'opcionOtro': forms.CheckboxInput(attrs={'class': 'checkbox-principal form-check-input', 'title': 'Habilitar Opción Otro', 'data-bs-original-title': 'Habilitar Opción Otro'}),            
            'numMin': forms.NumberInput(attrs={'class': 'opcion-digit form-control form-control-sm border-3' }),
            'numMax': forms.NumberInput(attrs={'class': 'opcion-digit form-control form-control-sm border-3' }),
            'row': forms.NumberInput(attrs={'class': 'form-control form-control-sm border-3', 'type': 'hidden'}),
            'col': forms.NumberInput(attrs={'class': 'form-control form-control-sm border-3', 'type': 'hidden'}),
            'tipo': forms.Select(attrs={'class': 'form-select form-select-sm border-3 elem-tipo-select', 'onchange': 'toggleElementoOpciones(this)', 'onload': 'toggleElementoOpciones(this)', 'placeholder': 'Tipo de pregunta'}),
        }
        labels = {
            'seccion': 'Sección',
            'nombre': 'Nombre de la Pregunta',
            'obligatorio': 'Obligatorio',        
            'opcionOtro': 'Opc. Otro',
            'numMin': 'Min. Dígitos', 
            'numMax': 'Max. Dígitos',
            'row': 'row',
            'col': 'col',
            'tipo': 'Tipo de Pregunta',            
        }
        
SeccionFormSet = modelformset_factory(Seccion, form=SeccionForm, extra=1, can_delete=True)
ElementoFormSet = inlineformset_factory(Seccion, Elemento, form=ElementoForm, extra=1, can_delete=True)
OpcionFormSet = inlineformset_factory(Elemento, Opcion, form=OpcionForm, extra=1, can_delete=True)


class RNumericoForm(forms.ModelForm):
    class Meta:
        model = RNumerico
        fields = ['texto']
        widgets = {'texto': forms.NumberInput(attrs={'class': 'form-control'}),}
        labels = {'texto': 'Respuesta numérica'}

class RTextoCortoForm(forms.ModelForm):
    class Meta:
        model = RTextoCorto
        fields = ['texto']
        widgets = {'texto': forms.TextInput(attrs={'class': 'form-control'}),}
        labels = {'texto': 'Respuesta texto corto'}

class RTextoParrafoForm(forms.ModelForm):
    class Meta:
        model = RTextoParrafo
        fields = ['texto']
        widgets = {'texto': forms.Textarea(attrs={'class': 'form-control'}),}
        labels = {'texto': 'Respuesta párrafo'}

class RHoraForm(forms.ModelForm):
    class Meta:
        model = RHora
        fields = ['hora']
        widgets = {'hora': forms.TimeInput(attrs={'class': 'form-control'}),}
        labels = {'hora': 'Hora'}

class RFechaForm(forms.ModelForm):
    class Meta:
        model = RFecha
        fields = ['fecha']
        widgets = {'fecha': forms.DateInput(attrs={'class': 'form-control'}),}
        labels = {'fecha': 'Fecha'}

class ROpcionMultipleForm(forms.ModelForm):
    class Meta:
        model = ROpcionMultiple
        fields = ['respuesta', 'otro']
        widgets = {'respuesta': forms.Select(attrs={'class': 'form-control'}),
                   'otro': forms.TextInput(attrs={'class': 'form-control'}),}
        labels = {'respuesta': 'Respuesta de opción múltiple', 'otro': 'Otro'}

class RCasillasForm(forms.ModelForm):
    class Meta:
        model = RCasillas
        fields = ['respuestas', 'otro']
        widgets = {'respuestas': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
                   'otro': forms.TextInput(attrs={'class': 'form-control'}),}
        labels = {'respuestas': 'Casillas', 'otro': 'Otro'}

class RDesplegableForm(forms.ModelForm):
    class Meta:
        model = RDesplegable
        fields = ['respuesta', 'otro']
        widgets = {'respuesta': forms.Select(attrs={'class': 'form-control'}),
                   'otro': forms.TextInput(attrs={'class': 'form-control'}),}
        labels = {'respuesta': 'Respuesta de desplegable', 'otro': 'Otro'}