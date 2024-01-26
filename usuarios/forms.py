from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import modelformset_factory
from django.forms import inlineformset_factory

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
    curp = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'CURP'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Correo electrónico'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Confirme su contraseña'}))
    

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
            'nombre': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese Nombre'}),
            'rfc': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese el RFC'}),
            'ap_paterno': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese el apellido paterno'}),
            'ap_materno': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese el apellido materno'}),
            'fecha_nacimiento': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control border-1', 'type': 'date'}),
            'genero': forms.Select(attrs={'class': 'form-control border-1 form-select'}),
            'g_etnico': forms.CheckboxInput(attrs={'class': 'form-check-input border-1'}),
            'municipio': forms.Select(attrs={'class': 'form-control form-select border-1'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese la colonia'}),
            'calle': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese la calle'}),
            'numero': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese el número'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control border-1', 'onkeydown': "return isNumberKey(event)", 'placeholder': 'Ingrese el código postal'}),
            'tel_cel': forms.TextInput(attrs={'class': 'form-control border-1', 'onkeypress': "return isNumberKey(event)", 'placeholder': 'Ingrese el teléfono celular'}),
            'tel_fijo': forms.TextInput(attrs={'class': 'form-control border-1', 'onkeypress': "return isNumberKey(event)", 'placeholder': 'Ingrese el teléfono fijo'}),
            'grado': forms.Select(attrs={'class': 'form-control border-1 form-select'}),
            'promedio': forms.NumberInput(attrs={'class': 'form-control border-1', 'onkeypress': "return isNumberPuntKey(event)", 'placeholder': 'Ingrese el promedio'}),
            'carrera': forms.Select(attrs={'class': 'form-control border-1 form-select'}),        
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
            'grado': 'Semestre/Cuatrimestre',
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
            if self.instance.municipio:          
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
            if self.instance.carrera:
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

class PuntajesGeneralesForm(forms.ModelForm):
    class Meta:
        model = PuntajeGeneral
        fields = ['tipo', 'nombre', 'puntos']
        labels = {
            'tipo': 'Tipo de seccion',
            'nombre': 'Nombre del Puntaje',
            'puntos': 'Puntos Asignados',
        }
        widgets = {
            'tipo': forms.HiddenInput(), 
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm form-control-label text-center px-0 fondo-gris-0'}),
            'puntos': forms.NumberInput(attrs={'class': 'form-control form-control-sm text-center m-auto', 'style': 'width: 5rem;'}),
        }

PuntajesGeneralesFormSet = modelformset_factory(
    PuntajeGeneral,
    form=PuntajesGeneralesForm,
    extra=0, 
    can_delete=True
)

class PuntajeMunicipioForm(forms.ModelForm):
    class Meta:
        model = PuntajeMunicipio
        fields = ['municipio', 'puntos']
        widgets = {
            'municipio': forms.Select(attrs={'class': 'form-control border-1 form-select', 'onchange': 'cargarMunicipio()'}),
            'puntos': forms.NumberInput(attrs={'class': 'form-control border-1 text-center m-auto', 'style': 'width: 5rem;'}),            
        }
    
    estado = forms.ModelChoiceField(queryset=Estado.objects.all(), empty_label="Selecciona un estado", widget=forms.Select(attrs={'class': 'form-control border-3 form-select', 'onchange': 'cargarMunicipio()'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['municipio'].queryset = Municipio.objects.none()
        if 'municipio' in self.data and self.data.get('municipio'):
            municipio_id = int(self.data.get('municipio'))
            municipios = (Municipio.objects.get(pk=municipio_id)).estado.municipio_set.all().order_by('nombre')                
            self.fields['municipio'].queryset = municipios
        elif self.instance.pk:
            municipios = self.instance.municipio.estado.municipio_set.all().order_by('nombre')                
            self.fields['municipio'].queryset = municipios    


    def set_estado(self, estado_id):
        if estado_id:
            municipios = Municipio.objects.filter(estado=estado_id)
            municipios_con_puntajes = PuntajeMunicipio.objects.filter(municipio__estado=estado_id)
            choices = [('', 'Selecciona un municipio')]  # Opción por defecto
            for muni in municipios:                
                try:
                    puntaje = PuntajeMunicipio.objects.get(municipio=muni)
                except PuntajeMunicipio.DoesNotExist:
                    puntaje = None
                nombre_municipio = muni.nombre
                if puntaje:                    
                    puntos = puntaje.puntos if puntaje.puntos is not None else 0
                    choice = (muni.id, f"{nombre_municipio} - Puntos: {puntos}")
                else:
                    choice = (muni.id, f"{nombre_municipio} - Puntos: {0}")
                choices.append(choice)
            self.fields['municipio'].choices = choices
            self.initial['estado'] = estado_id  # Establece el valor inicial del campo estado

class InstitucionForm(forms.ModelForm):
    class Meta:
        model = Institucion
        fields = ['nombre', 'puntos'] 
        labels = {
            'nombre': 'Nombre de la Institución', 
            'puntos': 'Puntos',  
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control border-1', 'placeholder': 'Ingrese nombre de la institución'}),  
            'puntos': forms.NumberInput(attrs={'class': 'form-control border-1' }),  
        }

class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = ['nombre', 'puntos', ]
        labels = {
            'nombre': 'Nombre carrera',
            'puntos': 'Puntos',
            
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control border-1', 'style': 'width: 21rem;','placeholder': 'Nombre de la carrera'}),
            'puntos': forms.NumberInput(attrs={'class': 'form-control border-1 m-0', 'style': 'width: 5rem;'}),            
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['title'] = self[field_name].value()

CarreraInlineFormSet = inlineformset_factory(Institucion, Carrera, form=CarreraForm, extra=1, can_delete=True)

class AgregarAdminForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['curp', 'nombre' , 'email', 'password1', 'password2','is_staff', 'is_superuser']
        labels = {
            'curp': 'CURP',
            'nombre': 'Nombre/Alias',
            'email' : 'Correo electrónico',
            'password1' : 'Contraseña',
            'password2' : 'Confirmar contraseña',
            'is_staff' : 'Es parte del departamento de estimulos',
            'is_superuser' : 'Administrador',
        }
        widgets = {
            'curp' : forms.TextInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Ingrese su CURP'}),
            'nombre' : forms.TextInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Ingrese un nombre o alias'}),
            'email' : forms.TextInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Ingrese su correo electrónico'}),
            'is_staff' : forms.CheckboxInput(attrs={'class': ''}),
            'is_superuser' : forms.CheckboxInput(attrs={'class': '', }),
        }
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Contraseña'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-3', 'placeholder': 'Confirme su contraseña'}))