from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import models
from .forms import *
from .models import *
from .views import verificarRedirect, borrarSelect

@login_required
def inicio(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    return render(request, 'admin/inicio.html')

@login_required
def solicitudes(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/solicitudes.html')

@login_required
def estadisticas(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/estadisticas.html')


#funcion recursiva para generar los nombres de los campos y los campos relacionados
def get_related_fields(field, prefix=''):
    if isinstance(field, models.ForeignKey):
        related_model = field.related_model
        related_fields = get_model_fields(related_model, prefix+field.name+'__')
        return related_fields
    elif isinstance(field, (models.ManyToOneRel, models.ManyToManyField)):
        return []
    else:        
        return [prefix + field.name]

#funcion recursiva para generar los nombres de los campos y los campos relacionados
def get_model_fields(model, prefix=''):
    fields = []
    for field in model._meta.get_fields():
        fields.extend(get_related_fields(field, prefix))
    return fields

#Metodo para filtrar un queryset en base a un string de palabras clave a buscar en sus campos
def BusquedaEnCamposQuerySet(queryset, search_query):  
    search_terms = search_query.split()     
    model = queryset.model 
    fields = get_model_fields(model)        

    q_objects = Q()
    for term in search_terms:
        for field in fields:            
            q_objects |= Q(**{f'{field}__icontains': term})
    queryset = queryset.filter(q_objects)         
    return queryset

@login_required
def listaUsuarios(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    request.session['anterior'] = request.build_absolute_uri()
    usuarios = Usuario.objects.filter(is_superuser=True)
    solicitantes = Solicitante.objects.all()

    if (request.method == 'GET'):
        search_query = request.GET.get('search', '')    
        #Si se hizo una busqueda de filtrado     
        if search_query:                                      
            solicitantes = BusquedaEnCamposQuerySet(solicitantes, search_query)
            usuarios = BusquedaEnCamposQuerySet(usuarios, search_query)                             

    paginator = Paginator(usuarios, 10)  # Mostrar 10 usuarios por página
    page_number = request.GET.get('pageA')
    page_admin= paginator.get_page(page_number)
    
    paginator = Paginator(solicitantes, 10)  # Mostrar 10 usuarios por página
    page_number = request.GET.get('pageS')
    page_soli= paginator.get_page(page_number)

    context = {
        'page_admin': page_admin,
        'page_soli': page_soli,
    }
    return render(request, 'admin/usuarios.html', context)


@login_required
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

@login_required
def configuracion(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    return render(request, 'admin/configuracion.html')

@login_required
def eliminarUsuario(request, user_id):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    user_to_delete = get_object_or_404(User, pk=user_id)    
    user_to_delete.delete()
    #print('usuario '+ str(user_to_delete) + ' eliminado')    
    anterior_url = request.session.get('anterior', "usuarios:AUsuarios")
    return redirect(anterior_url)