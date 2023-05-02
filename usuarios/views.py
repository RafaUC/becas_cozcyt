from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.

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
