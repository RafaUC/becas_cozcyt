from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.

def login(request):
    if request.method == "POST":
        pass
    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        pass
    return render(request, 'register.html')
