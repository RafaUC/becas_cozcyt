from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404

# Create your views here.
from .forms import CreateUserForm
from .models import *
from django.urls import reverse_lazy


def login(request):
    if request.method == "POST":
        pass
    return render(request, "login.html")

def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(data=request.POST)
        if form.is_valid():
            print('valid')
            form.save()
            return render(request, "login.html") #cambiar a la vista de confirmar email cuando se tenga implementada
        else:
            print('not valid')
    context = {'form' : form}
    return render(request, 'register.html', context)
