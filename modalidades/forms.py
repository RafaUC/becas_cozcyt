from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from .models import Modalidad

from .models import *

class ModalidadForm(ModelForm):
    error_css_class = 'error-field'
    required_css_class = 'required-field'
    class Meta:
        model = Modalidad
        fields = ('nombre', 'imagen', 'descripcion')
        labels = {
            'nombre': '',
            'imagen' : '',
            'descripcion': '',
        }
        widgets = {
            'nombre' : forms.TextInput(attrs={'class': 'form-control mt-1', 'placeholder': 'Ej. Talento especial, LABSOL...'}),
            'descripcion' : forms.Textarea(attrs={'class': 'form-control mt-1', 'placeholder': 'Ej. Modalidad que se le otorga a los estudiantes que...', 'rows':3, 'cols':1})
        }

class DocumentoForm(ModelForm):
    class Meta:
        model = Documento
        fields = ('nombre', 'descripcion')
        labels = {
            'nombre': '',
            'descripcion': '',
        }
        widgets = {
            'nombre' : forms.TextInput(attrs={'class': 'form-control mt-1', 'placeholder': 'Nombre de documento' , 'style': 'text-align: center;'}),
            'descripcion' : forms.Textarea(attrs={'class': 'form-control mt-1', 'placeholder': 'Descripción del documento', 'rows':3, 'cols':1})
        }
