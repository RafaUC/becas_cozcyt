from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import *
from .models import *
from django.urls import reverse_lazy



def verificarPrimerLogin(usuario):
    print('en verificar')
    if usuario.has_perm('permiso_administrador') and usuario.is_superuser == 1:
        print('es admin')
        return
    elif Solicitante.objects.filter(id=usuario.id).exists():
        print('solicitante ya existe')
        return
    else:
        print('nuevo solicitante')
        return ("usuarios:primer_login")

def loginSistema(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():            
            #Se intenta autenticar el usuario con las credenciales y obtener su objeto
            try:                 
                usuario = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])                                                            
            except Exception as e:                       
                usuario = None            
            #si el usuario existe y se autentico
            if usuario is not None:                                
                login(request, usuario)
                messages.success(request, "Sesion iniciada correctamente.")                
                verificarPrimerLogin(usuario)                
                succes_url = verificarPrimerLogin(usuario)
                if succes_url is None:                    
                    if 'next' in request.GET:                    
                        succes_url = request.GET['next']
                    else:                    
                        succes_url = settings.LOGIN_REDIRECT_URL
                return redirect(succes_url)
        else:            
            messages.error(request, "CURP o contraseña incorrectos.")            
    context = {'form' : form}
    return render(request, "login.html", context)


def cerrarSesion(request):
    logout(request)
    return redirect(settings.LOGIN_URL)

def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(data = request.POST)
        if form.is_valid():
            #print('valid')
            form.save()
            return render(request, "login.html") #cambiar a la vista de confirmar email cuando se tenga implementada
        else:
            #print('not valid')
            messages.error(request, " ")
    context = {'form' : form}
    return render(request, 'register.html', context)

@login_required
def primerLogin(request):
    usuario = get_object_or_404(Usuario, id=request.user.id)
    form = SolicitanteForm()
    estadoSelectForm = EstadoSelectForm()
    institucionSelectForm = InstitucionSelectForm()

    if usuario.has_perm('permiso_administrador') and usuario.is_superuser == 1:
        return redirect(settings.LOGIN_REDIRECT_URL)   
    elif Solicitante.objects.filter(id=usuario.id).exists():
        print('solicitante ya existe')
        return redirect(settings.LOGIN_REDIRECT_URL)  

    if request.method == 'POST':
        form = SolicitanteForm(data = request.POST)
        estadoSelectForm = EstadoSelectForm(data = request.POST)   
        institucionSelectForm = InstitucionSelectForm(data = request.POST)
        estadoSelectForm.errors.as_data()
        if form.is_valid() and estadoSelectForm.is_valid() and institucionSelectForm.is_valid():   
            print('intentndo guardar')         
            solicitante = form.save(commit=False)
            solicitante.pk = usuario.pk
            solicitante.__dict__.update(usuario.__dict__)            
            solicitante.save()
            return redirect(settings.LOGIN_REDIRECT_URL)       
        else:    #el formulario no es valido
            print('no es valido')
            print(form.errors.as_data())
            print(estadoSelectForm.errors.as_data())
            print(institucionSelectForm.errors.as_data())            
            borrarSelect(form, estadoSelectForm, 'municipio', 'estado')
            borrarSelect(form, institucionSelectForm, 'carrera', 'institucion')
    context = {'form' : form,
               'estadoSelectForm' : estadoSelectForm,
               'institucionSelectForm': institucionSelectForm}
    return render(request, 'primer_login.html', context)

def cargar_select_list(request, app, modDep, modIndep, orderBy='id'):
    estado_id = request.GET.get(modIndep)
    modelo = apps.get_model(app, modDep)
    columna = modIndep+'_id'
    try:                     
        query = modelo.objects.filter(**{columna: estado_id}).order_by(orderBy)        
    except Exception as e:      
        print(e)  
        query = Municipio.objects.none()    
    return render(request, 'select_list.html', {'query': query})

def borrarSelect(formDep, formIndep, campoDep, campoIndep):
    if formDep.has_error(campoDep):         #se verifica que el select dependiente (municipio) tenga errores,
        _mutable = formDep.data._mutable       #si asi es se procede a dejar en blanco esos selects relacionados
        formDep.data._mutable = True                        
        formDep.data[campoDep] = ''
        formDep.data._mutable = _mutable

        _mutable = formIndep.data._mutable
        formIndep.data._mutable = True                        
        formIndep.data[campoIndep] = ''
        formIndep.data._mutable = _mutable   

@login_required
def perfil(request):
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    rfc = solicitante.rfc      
    formPersonal = SolicitantePersonalesForm(instance = solicitante) #asegurarse de no modificar el rfc
    formDomicilio = SolicitanteDomicilioForm(instance = solicitante)
    formEscolar = SolicitanteEscolaresForm(instance = solicitante)
    estadoSelectForm = EstadoSelectForm(initial={'estado': solicitante.municipio.estado.pk})
    institucionSelectForm = InstitucionSelectForm(initial={'institucion': solicitante.carrera.institucion.pk})
    if request.method == 'POST':
        boton = request.POST.get('guardar', None)
        if boton == 'personal':
            post = request.POST.copy()
            post['rfc'] = rfc
            formPersonal = SolicitantePersonalesForm(post, instance=solicitante)             
            if formPersonal.is_valid():
                solicitante = formPersonal.save(commit=False)
                solicitante.rfc = rfc
                solicitante.save()
                return redirect("usuarios:perfil")  

        elif boton == 'domicilio':
            estadoSelectForm = EstadoSelectForm(data = request.POST)   
            formDomicilio = SolicitanteDomicilioForm(request.POST, instance=solicitante) 
            if formDomicilio.is_valid() and estadoSelectForm.is_valid():
                formDomicilio.save()
                return redirect("usuarios:perfil")  
            else:    #el formulario no es valido                             
                borrarSelect(formDomicilio, estadoSelectForm, 'municipio', 'estado')                

        elif boton == 'escolar':
            institucionSelectForm = InstitucionSelectForm(data = request.POST)
            formEscolar = SolicitanteEscolaresForm(request.POST, instance=solicitante) 
            if formEscolar.is_valid() and institucionSelectForm.is_valid():
                formEscolar.save()
                return redirect("usuarios:perfil")  
            else:    #el formulario no es valido                                
                borrarSelect(formEscolar, institucionSelectForm, 'carrera', 'institucion')
        
        
        estadoSelectForm.errors.as_data()                         
        
    context = {'estadoSelectForm' : estadoSelectForm,
               'institucionSelectForm': institucionSelectForm,
               'formPersonal': formPersonal,
               'formDomicilio': formDomicilio,
               'formEscolar': formEscolar}
    return render(request, 'perfil.html', context)

