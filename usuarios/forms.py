from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Usuario
from django.contrib.auth import get_user_model
User = get_user_model()

class CreateUserForm(UserCreationForm):
    class Meta:
        model = Usuario
        exclude = ('nombre', 'is_staff')
        fields = ('curp', 'email', 'password1', 'password2')