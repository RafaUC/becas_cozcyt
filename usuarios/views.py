from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.apps import apps
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.http import HttpResponse  
from django.core.files.storage import FileSystemStorage

from .forms import *
from .models import *
from .tokens import account_activation_token
from modalidades.models import *
from modalidades.forms import *
from .decorators import user_passes_test, user_passes_test_httpresponse, usuarioEsSolicitante

def rootRedirect(request):   
    return redirect('transparencia:Tinicio')

@login_required
def loginRedirect(request):    
    usuario = get_object_or_404(Usuario, id=request.user.id)
    solicitante = Solicitante.objects.filter(id=usuario.id).first() #obtenermos el solisitante si es que existe
    if usuario.has_perm('permiso_administrador') and usuario.is_superuser == 1:    
        return redirect("usuarios:AInicio")
    elif not solicitante or (solicitante and not solicitante.info_completada ):        
        return redirect("usuarios:primer_login")
    else:
        return redirect("solicitudes:convocatorias")
    
#Verifica que el usuario tiene los permisos o el estado para estar en esa view, si no, retorna la url donde deberia ser redirigido
#si no se dan permisos en el parametro permisos significa que no requere ningun permiso pero no puede entrar un admin
#DEPRECADO
def verificarRedirect_(usuario, *permisos):    
    """if not any(usuario.has_perm(perm) for perm in permisos):  #el no usuario tiene permiso de estar en la pagina
        return settings.LOGIN_REDIRECT_URL """    
    if (not usuario.has_perm('permiso_administrador')) and ('permiso_administrador' in permisos): # el usuario no es admin y se requiere un admin        
        return settings.LOGIN_REDIRECT_URL
    elif usuario.has_perm('permiso_administrador') and ('permiso_administrador' not in permisos): #el usuario es admin pero los administradores no puede estar en la view
        return settings.LOGIN_REDIRECT_URL
    elif not Solicitante.objects.filter(id=usuario.id).exists() and (not usuario.has_perm('permiso_administrador')):   # el solicitante no existe y por lo tanto no ha completado su informacion persoanl
        #print('nuevo solicitante')
        return "usuarios:primer_login"
    elif Solicitante.objects.filter(id=usuario.id).exists() and not Solicitante.objects.get(pk=usuario.id).info_completada :
        #print('login incompleto')
        return "usuarios:primer_login"
    else: #si ningun caso anterior se ejecuto significa que el usuario puede estar en la view actual
        return
        

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
                return redirect(settings.LOGIN_REDIRECT_URL)
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
        #Si un usuario no verificado intenta volver a registrarse, se intenta reusar ese usuario y reenviar el correo al nuevo correo
        usrCurp = Usuario.objects.filter(is_active=False, curp=request.POST.get('curp')).first()        
        usrEmail = Usuario.objects.filter(is_active=False, email=request.POST.get('email')).exclude(curp=request.POST.get('curp')).first()                
        if usrEmail:           
           usrEmail.delete()

        form = CreateUserForm(data = request.POST, instance=usrCurp)
        if form.is_valid():
            #Hacer que el registro válido se guarda en la memoria, no en la base de datos
            user = form.save(commit=False)
            user.is_active = False 
            user.save()
            #print(form.cleaned_data.get('email'))
            mail_subject = 'Confirmar cuenta'  
            message = render_to_string('email.html', {  
                'user': user,  
                'domain': get_current_site(request).domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            )  
            email.content_subtype = 'html'
            email.send()  #comentar esta linea para si no se desea mandar el correo
            messages.success(request, 'Le enviamos un correo a su dirección de email para verificar su cuenta. Si no visualiza ningún correo, revise su carpeta de spam.')
            return redirect("usuarios:login")  
            # return render(request, 'confirmar_email.html')
            #return HttpResponse('Please confirm your email address to complete the registration') 
        else:
            #print('not valid')
            #for error in list (form.errors.values()):
            messages.error(request, form.errors)
    context = {'form' : form}
    return render(request, 'register.html', context)

def activate(request, uidb64, token):
    usuario = get_user_model()
    try :
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = usuario.objects.get(pk=uid)
    except:
        user = None
    #print(f'{uid} {token} || user {user}, accval {account_activation_token.check_token(user,token)} ')
    if user is not None and account_activation_token.check_token(user,token):        
        user.is_active = True    
        user.save()
        print('Correo confirmado')
        messages.success(request, 'Correo electrónico y cuenta confirmados. Ya puede iniciar sesión.')
        return redirect("usuarios:login")        
    else:  
        if user and user.is_active:
            messages.success(request, 'El correo electrónico y cuenta ya se encuentran confirmados. Ya puede iniciar sesión.')
            return redirect("usuarios:login")    
        else :
            return HttpResponse('Link inválido o no disponible.')  

@login_required
def primerLogin(request):
    usuario = get_object_or_404(Usuario, id=request.user.id)
    solicitante = Solicitante.objects.filter(id=request.user.id).first()
    form = SolicitanteForm()
    estadoSelectForm = EstadoSelectForm()
    institucionSelectForm = InstitucionSelectForm()

    if solicitante :
        form = SolicitanteForm(instance=solicitante)
        if solicitante.municipio:
            estadoSelectForm = EstadoSelectForm(initial={'estado': solicitante.municipio.estado.pk})                    
        if solicitante.carrera :
            institucionSelectForm = InstitucionSelectForm(initial={'institucion': solicitante.carrera.institucion.pk})                
        

    if usuario.has_perm('permiso_administrador') and usuario.is_superuser == 1:
        return redirect(settings.LOGIN_REDIRECT_URL)   
    elif Solicitante.objects.filter(id=usuario.id).exists() and Solicitante.objects.get(pk=usuario.id).info_completada:        
        return redirect(settings.LOGIN_REDIRECT_URL)      

    if request.method == 'POST':
        form = SolicitanteForm(data = request.POST)
        estadoSelectForm = EstadoSelectForm(data = request.POST)   
        institucionSelectForm = InstitucionSelectForm(data = request.POST)
        if solicitante :
            form = SolicitanteForm(request.POST, instance=solicitante)
            if solicitante.municipio:
                estadoSelectForm = EstadoSelectForm(request.POST, initial={'estado': solicitante.municipio.estado.pk})                    
            if solicitante.carrera :
                institucionSelectForm = InstitucionSelectForm(request.POST, initial={'institucion': solicitante.carrera.institucion.pk})                
            
        estadoSelectForm.errors.as_data()
        if form.is_valid() and estadoSelectForm.is_valid() and institucionSelectForm.is_valid():                        
            solicitante = form.save(commit=False)
            solicitante.pk = usuario.pk
            nombre = request.POST.get('nombre')     
            usuario.__dict__.update({'nombre': nombre})
            solicitante.__dict__.update(usuario.__dict__)  
            solicitante.save()
            messages.success(request, 'Perfil completado con éxito')
            return redirect(settings.LOGIN_REDIRECT_URL)       
        else:    #el formulario no es valido          
            messages.error(request, form.errors)          
            borrarSelect(form, estadoSelectForm, 'municipio', 'estado')
            borrarSelect(form, institucionSelectForm, 'carrera', 'institucion')
    context = {'form' : form,
               'estadoSelectForm' : estadoSelectForm,
               'institucionSelectForm': institucionSelectForm}
    return render(request, 'primer_login.html', context)

def cargar_select_list(request, app, modDep, modIndep, orderBy='id'):
    mod_Indep = request.GET.get(modIndep)
    modelo = apps.get_model(app, modDep)
    columna = modIndep+'_id'
    try:                     
        query = modelo.objects.filter(**{columna: mod_Indep}).order_by(orderBy)        
    except Exception as e:              
        query = modelo.objects.none()    
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
@user_passes_test(usuarioEsSolicitante, login_url='usuarios:loginRedirect')
def perfil(request):      
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #rfc = solicitante.rfc      
    formPersonal = SolicitantePersonalesForm(instance = solicitante) #asegurarse de no modificar el rfc
    formDomicilio = SolicitanteDomicilioForm(instance = solicitante)
    formEscolar = SolicitanteEscolaresForm(instance = solicitante)
    if solicitante.municipio:
        estadoSelectForm = EstadoSelectForm(initial={'estado': solicitante.municipio.estado.pk})
    else :
        estadoSelectForm = EstadoSelectForm()
    if solicitante.carrera:
        institucionSelectForm = InstitucionSelectForm(initial={'institucion': solicitante.carrera.institucion.pk})
    else:
        institucionSelectForm = InstitucionSelectForm()
    

    if request.method == 'POST':
        boton = request.POST.get('guardar', None)
        if boton == 'personal':
            post = request.POST.copy()
            #post['rfc'] = rfc
            formPersonal = SolicitantePersonalesForm(post, instance=solicitante)             
            if formPersonal.is_valid():
                solicitante = formPersonal.save(commit=False)
                #solicitante.rfc = rfc
                solicitante.save()
                messages.success(request, 'Perfil actualizado con éxito')
                return redirect("usuarios:perfil")  
            else:
                messages.error(request, formPersonal.errors)

        elif boton == 'domicilio':
            estadoSelectForm = EstadoSelectForm(data = request.POST)   
            formDomicilio = SolicitanteDomicilioForm(request.POST, instance=solicitante) 
            if formDomicilio.is_valid() and estadoSelectForm.is_valid():
                formDomicilio.save()
                messages.success(request, 'Perfil actualizado con éxito')
                return redirect("usuarios:perfil")  
            else:    #el formulario no es valido                             
                borrarSelect(formDomicilio, estadoSelectForm, 'municipio', 'estado')                
                messages.error(request, formDomicilio.errors)
                messages.error(request, estadoSelectForm.errors)

        elif boton == 'escolar':
            institucionSelectForm = InstitucionSelectForm(data = request.POST)
            formEscolar = SolicitanteEscolaresForm(request.POST, instance=solicitante) 
            if formEscolar.is_valid() and institucionSelectForm.is_valid():
                formEscolar.save()
                messages.success(request, 'Perfil actualizado con éxito')
                return redirect("usuarios:perfil")  
            else:    #el formulario no es valido                                
                borrarSelect(formEscolar, institucionSelectForm, 'carrera', 'institucion')
                messages.error(request, formEscolar.errors)
                messages.error(request, institucionSelectForm.errors)
        
        
        estadoSelectForm.errors.as_data()                         
        
    for field in formPersonal.fields.values():
        field.widget.attrs['disabled'] = 'disabled'
    for field in formDomicilio.fields.values():
        field.widget.attrs['disabled'] = 'disabled'
    for field in formEscolar.fields.values():
        field.widget.attrs['disabled'] = 'disabled'
    for field in estadoSelectForm.fields.values():
        field.widget.attrs['disabled'] = 'disabled'
    for field in institucionSelectForm.fields.values():
        field.widget.attrs['disabled'] = 'disabled'
    
    context = {'estadoSelectForm' : estadoSelectForm,
               'institucionSelectForm': institucionSelectForm,
               'formPersonal': formPersonal,
               'formDomicilio': formDomicilio,
               'formEscolar': formEscolar}
    return render(request, 'solicitante/perfil.html', context)

@login_required
@user_passes_test(usuarioEsSolicitante, login_url='usuarios:loginRedirect')
def sMensajes(request):    
    return render(request, 'solicitante/sMensajes.html')

