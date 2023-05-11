from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404

# Create your views here.
from .forms import CreateUserForm, LoginForm
from .models import *
from django.urls import reverse_lazy


def loginSistema(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            print("is valid")
            try: 
                print(form.cleaned_data['username'])
                print(form.cleaned_data['password'])
                usuario = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])                        
                #usuario = authenticate(username=request.POST.get('curp'), password=request.POST.get('password'))                        
            except Exception as e:    
                print(e)        
                usuario = None            
            if usuario is not None:
                login(request, usuario)
                messages.success(request, "Sesion iniciada correctamente.")
                return redirect("admin:index")            
        else:
            messages.error(request, "CURP o contraseña incorrectos.")            
    context = {'form' : form}
    return render(request, "login.html", context)

def register(request): #Checar los permisos
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(data = request.POST)
        if form.is_valid():
            #print('valid')
            form.save()
            return redirect("confirmar_email/")
        else:
            #print('not valid')
            messages.error(request, " ")
    context = {'form' : form}
    return render(request, 'register.html', context)

def perfil(request):
    return render(request, 'perfil.html')

def confirmar(request):
    return render(request, 'confirmar_email.html')