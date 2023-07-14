from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import *
from .models import *
from .views import verificarRedirect, borrarSelect

def inicio(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    return render(request, 'admin/inicio.html')


def solicitudes(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/solicitudes.html')


def estadisticas(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/estadisticas.html')


def listaUsuarios(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/usuarios.html')

def editarUsuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=pk)  
    #rfc = solicitante.rfc      
    formPersonal = SolicitantePersonalesForm(instance = solicitante) #asegurarse de no modificar el rfc
    formDomicilio = SolicitanteDomicilioForm(instance = solicitante)
    formEscolar = SolicitanteEscolaresForm(instance = solicitante)
    estadoSelectForm = EstadoSelectForm(initial={'estado': solicitante.municipio.estado.pk})
    institucionSelectForm = InstitucionSelectForm(initial={'institucion': solicitante.carrera.institucion.pk})
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

    if request.method == 'POST':
        url = request.get_full_path()        
        boton = request.POST.get('guardar', None)
        if boton == 'personal':
            post = request.POST.copy()
            #post['rfc'] = rfc
            formPersonal = SolicitantePersonalesForm(post, instance=solicitante)             
            if formPersonal.is_valid():
                solicitante = formPersonal.save(commit=False)
                #solicitante.rfc = rfc
                solicitante.save()
                return redirect(url)

        elif boton == 'domicilio':
            estadoSelectForm = EstadoSelectForm(data = request.POST)   
            formDomicilio = SolicitanteDomicilioForm(request.POST, instance=solicitante) 
            if formDomicilio.is_valid() and estadoSelectForm.is_valid():
                formDomicilio.save()
                return redirect(url)
            else:    #el formulario no es valido                             
                borrarSelect(formDomicilio, estadoSelectForm, 'municipio', 'estado')                

        elif boton == 'escolar':
            institucionSelectForm = InstitucionSelectForm(data = request.POST)
            formEscolar = SolicitanteEscolaresForm(request.POST, instance=solicitante) 
            if formEscolar.is_valid() and institucionSelectForm.is_valid():
                formEscolar.save()
                return redirect(url)
            else:    #el formulario no es valido                                
                borrarSelect(formEscolar, institucionSelectForm, 'carrera', 'institucion')
        
        
        estadoSelectForm.errors.as_data()                         
        
    context = {'curp' : solicitante.curp,
               'estadoSelectForm' : estadoSelectForm,
               'institucionSelectForm': institucionSelectForm,
               'formPersonal': formPersonal,
               'formDomicilio': formDomicilio,
               'formEscolar': formEscolar}
    return render(request, 'admin/editar_usuario.html', context)


def configuracion(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/configuracion.html')