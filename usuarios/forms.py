from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

from .models import Usuario
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