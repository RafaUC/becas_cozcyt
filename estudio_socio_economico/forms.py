from django import forms
from .models import Seccion, Opcion, Elemento
from django.forms import inlineformset_factory, modelformset_factory



class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-lg font-semi-bold border-3'}),
            'tipo': forms.RadioSelect(attrs={'class': 'ms-3'}),
        }
        labels = {
            'nombre': 'Nombre de la Sección',
            'tipo': 'Tipo de la Sección',
        }
        
        

class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ['elemento', 'nombre']
        widgets = {
            'elemento': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'elemento': 'Elemento',
            'nombre': 'Nombre Opción',
        }
        
        

class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = ['seccion', 'nombre', 'obligatorio', 'row', 'col', 'tipo',]
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-control border-3', 'placeholder': 'Selecciona una sección'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control font-semi-bold border-3 ', 'placeholder': 'Nombre de la pregunta'}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'checkbox-principal form-check-input'}),            
            'row': forms.NumberInput(attrs={'class': 'form-control border-3', 'type': 'hidden'}),
            'col': forms.NumberInput(attrs={'class': 'form-control border-3', 'type': 'hidden'}),
            'tipo': forms.Select(attrs={'class': 'form-select border-3', 'placeholder': 'Tipo de pregunta'}),
        }
        labels = {
            'seccion': 'Sección',
            'nombre': 'Nombre de la Pregunta',
            'obligatorio': 'Obligatorio',            
            'row': 'row',
            'col': 'col',
            'tipo': 'Tipo de Pregunta',            
        }
        
SeccionFormSet = modelformset_factory(Seccion, form=SeccionForm, extra=0, can_delete=True)
ElementoFormSet = inlineformset_factory(Seccion, Elemento, form=ElementoForm, extra=1, can_delete=True)

