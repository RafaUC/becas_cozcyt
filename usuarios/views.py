from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404

# Create your views here.
from .forms import CreateUserForm
from .models import *
from django.urls import reverse_lazy


def loginSistema(request):
    if request.method == "POST":
        try: 
            usuario = authenticate(username=request.POST.get('curp'), password=request.POST.get('password'))                        
        except Exception as e:            
            usuario = None            
        if usuario is not None:
            login(request, usuario)
            messages.success(request, "Sesion iniciada correctamente.")
            return redirect("admin:index")
        else:            
            messages.error(request, "CURP o contraseña incorrectos.")
            return redirect("usuarios:login")
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
