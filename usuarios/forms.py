from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg mt-3', 'placeholder': 'Curp'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Contraseña'}))
    error_messages = {
        'invalid_login': "Ingrese un %(username)s y contraseña validos. "
                           "Tenga en cuenta que estos campos distinguen entre mayúsculas y minúsculas.",
        'inactive': "Esta cuenta esta inactiva.",
    }
    
    class Meta:
        model = Usuario        

class CreateUserForm(UserCreationForm):
    class Meta:
        model = Usuario
        exclude = ('nombre', 'is_staff')
        fields = ('curp', 'email', 'password1', 'password2')

class EstadoSelectForm(forms.ModelForm):
    class Meta:
        model = Municipio
        fields = ('estado',)
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control form-select'}),
        }
        labels = {'estado': 'Estado', }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].queryset = self.fields['estado'].queryset.order_by('nombre')

class InstitucionSelectForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ('institucion',)
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-control form-select'}),
        }
        labels = {'institucion': 'Institución', }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['institucion'].queryset = self.fields['institucion'].queryset.order_by('nombre')

class SolicitanteForm(forms.ModelForm):
    class Meta:
        model = Solicitante
        fields = ['nombre',
                  'rfc', 
                  'ap_paterno', 
                  'ap_materno', 
                  'fecha_nacimiento', 
                  'genero', 
                  'g_etnico', 
                  'municipio', 
                  'colonia', 
                  'calle', 
                  'numero', 
                  'codigo_postal', 
                  'tel_cel', 
                  'tel_fijo', 
                  'grado', 
                  'promedio', 
                  'carrera']        
        widgets = {            
            'nombre': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese Nombre'}),
            'rfc': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese el RFC'}),
            'ap_paterno': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese el apellido paterno'}),
            'ap_materno': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese el apellido materno'}),
            'fecha_nacimiento': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control border-3', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-control border-3 form-select'}),
            'g_etnico': forms.CheckboxInput(attrs={'class': 'form-check-input border-3'}),
            'municipio': forms.Select(attrs={'class': 'form-control form-select border-3'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese la colonia'}),
            'calle': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese la calle'}),
            'numero': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Ingrese el número'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control border-3', 'onkeydown': "return isNumberKey(event)", 'placeholder': 'Ingrese el código postal'}),
            'tel_cel': forms.TextInput(attrs={'class': 'form-control border-3', 'onkeypress': "return isNumberKey(event)", 'placeholder': 'Ingrese el teléfono celular'}),
            'tel_fijo': forms.TextInput(attrs={'class': 'form-control border-3', 'onkeypress': "return isNumberKey(event)", 'placeholder': 'Ingrese el teléfono fijo'}),
            'grado': forms.Select(attrs={'class': 'form-control border-3 form-select'}),
            'promedio': forms.NumberInput(attrs={'class': 'form-control border-3', 'onkeypress': "return isNumberPuntKey(event)", 'placeholder': 'Ingrese el promedio'}),
            'carrera': forms.Select(attrs={'class': 'form-control border-3 form-select'}),        
        }
        labels = {
            'nombre': 'Nombre',
            'rfc': 'RFC',
            'ap_paterno': 'Apellido Paterno',
            'ap_materno': 'Apellido Materno',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'genero': 'Genero',
            'g_etnico': 'Grupo Etnico',
            'municipio': 'Delegación/Municipio',
            'colonia': 'Colonia/Fraccionamiento',
            'calle': 'Calle',
            'numero': 'Numero',
            'codigo_postal': 'Codigo Postal',
            'tel_cel': 'Telefono Celular',
            'tel_fijo': 'Telefono Fijo',
            'grado': 'Grado',
            'promedio': 'Promedio',
            'carrera': 'Carrera',            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'municipio' in self.fields:
            self.fields['municipio'].queryset = Municipio.objects.none()
        if 'carrera' in self.fields:
            self.fields['carrera'].queryset = Carrera.objects.none()

        if ('municipio' in self.data) and ('municipio' in self.fields):
            try:
                municipio_id = int(self.data.get('municipio'))
                municipios = (Municipio.objects.get(pk=municipio_id)).estado.municipio_set.all().order_by('nombre')                
                self.fields['municipio'].queryset = municipios
            except (ValueError, TypeError) as e:            
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and ('municipio' in self.fields):            
            municipios = self.instance.municipio.estado.municipio_set.all().order_by('nombre')                
            self.fields['municipio'].queryset = municipios       

        if ('carrera' in self.data) and ('carrera' in self.fields):
            try:
                carrera_id = int(self.data.get('carrera'))
                carreras = (Carrera.objects.get(pk=carrera_id)).institucion.carrera_set.all().order_by('nombre')                
                self.fields['carrera'].queryset = carreras
            except (ValueError, TypeError) as e:            
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk and ('carrera' in self.fields) :            
            carreras = self.instance.carrera.institucion.carrera_set.all().order_by('nombre')                
            self.fields['carrera'].queryset = carreras    

class SolicitantePersonalesForm(SolicitanteForm):    

    class Meta(SolicitanteForm.Meta):
        exclude = ('municipio', 
                  'colonia', 
                  'calle', 
                  'numero', 
                  'codigo_postal', 
                  'tel_cel', 
                  'tel_fijo', 
                  'grado', 
                  'promedio', 
                  'carrera')
           
    
        
class SolicitanteDomicilioForm(SolicitanteForm):
    class Meta(SolicitanteForm.Meta):
        exclude = ('nombre',
                  'rfc', 
                  'ap_paterno', 
                  'ap_materno', 
                  'fecha_nacimiento', 
                  'genero', 
                  'g_etnico', 
                  'grado', 
                  'promedio', 
                  'carrera')

class SolicitanteEscolaresForm(SolicitanteForm):
    class Meta(SolicitanteForm.Meta):
        exclude = ('nombre',
                  'rfc', 
                  'ap_paterno', 
                  'ap_materno', 
                  'fecha_nacimiento', 
                  'genero', 
                  'g_etnico', 
                  'municipio', 
                  'colonia', 
                  'calle', 
                  'numero', 
                  'codigo_postal', 
                  'tel_cel', 
                  'tel_fijo')