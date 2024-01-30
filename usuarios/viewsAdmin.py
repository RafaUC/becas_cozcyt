from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.apps import apps
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import models
from django.db.models import Count
from .forms import *
from .models import *
from .views import verificarRedirect, borrarSelect

from modalidades.models import *
from solicitudes.models import *

@login_required
def inicio(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    convocatoria = Convocatoria.objects.all().first()
    solicitudes = Solicitud.objects.filter(ciclo = ciclo_actual()) #aceptadas

    valoresFrecuencias = solicitudes.filter(estado=Solicitud.ESTADO_CHOICES[3][0]).values('modalidad__nombre', 'modalidad__monto').annotate(frecuencia=Count('modalidad__nombre'))            
    valoresFrecuencias = sorted(valoresFrecuencias, key=lambda x: x['frecuencia'], reverse=True)        
    total = 0           
    for item in valoresFrecuencias:        
        total += item['frecuencia'] * item['modalidad__monto']        

    presupuesto = 'Sin convocatoria'
    presupuestoRestante = 'Sin convocatoria'
    if convocatoria:
        presupuesto = f'${convocatoria.presupuesto:,.2f}'
        presupuestoRestante = f'${convocatoria.presupuesto-total:,.2f}'

    context = {
        'ciclo_actual': ciclo_actual(),
        'convocatoria' : convocatoria,
        'solicitudes' : len(solicitudes),
        'presupuesto': presupuesto,
        'presupuestoRestante': presupuestoRestante
    }

    return render(request, 'admin/inicio.html', context)





CLASE_CAMPOS_BUSQUEDA = {'foreignKey': models.ForeignKey, 'manyToOne': models.ManyToOneRel, 'manyToMany': models.ManyToManyField, 'oneToOne': models.OneToOneRel}

#funcion recursiva para generar los nombres de los campos y los campos relacionados
def get_related_fields(field, relatedFieldType, prefix='' ):       
    if isinstance(field, relatedFieldType):        
        related_model = field.related_model
        related_fields = get_model_fields(related_model, relatedFieldType, prefix+field.name+'__')
        return related_fields
    elif field.__class__ in CLASE_CAMPOS_BUSQUEDA.values():         
        return []
    else:                
        return [prefix + field.name]

#funcion recursiva para generar los nombres de los campos y los campos relacionados
def get_model_fields(model, relatedFieldType, prefix='' ):
    fields = []
    for field in model._meta.get_fields():
        fields.extend(get_related_fields(field, relatedFieldType, prefix))
    return fields

#Metodo para filtrar un queryset en base a un string de palabras clave a buscar en sus campos
def BusquedaEnCamposQuerySet(queryset, search_query, relatedFieldType=CLASE_CAMPOS_BUSQUEDA['foreignKey']):  
    search_terms = search_query.split()     
    model = queryset.model 
    fields = get_model_fields(model, relatedFieldType)  
       
    
    q_objects = Q()
    exclude_objects = Q()

    for term in search_terms:
        term_query = Q()        
        is_exclude = term.startswith('-')  # Verifica si el término comienza con '-'
        is_or = term.startswith('~')  # Verifica si el término comienza con '~' para OR
        term = term[1:] if is_exclude or is_or else term
        
        for field in fields:
            if ':' in term:
                campo, valor = term.split(':', 1)
                if campo == 'nombre' and ('nombre' == field or 'solicitante__nombre' in field):                    
                    term_query |= Q(**{f'{field}__icontains': valor})
                elif campo != 'nombre' and campo in field:                                            
                    term_query |= Q(**{f'{field}__icontains': valor})                
            else:
                term_query |= Q(**{f'{field}__icontains': term})        

        if is_exclude:  # Agrega la condición al objeto de exclusión o al objeto de inclusión
            exclude_objects &= term_query
        elif is_or:  # Realiza un OR con los términos de búsqueda
            q_objects |= term_query
        else:
            q_objects &= term_query
    
    if search_terms and not q_objects:
        queryset = model.objects.none()
    else:
        queryset = queryset.filter(q_objects).exclude(exclude_objects)
    return queryset

@login_required
def listaInstituciones(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    request.session['anterior'] = request.build_absolute_uri()       
    instituciones = Institucion.objects.all()

    if (request.method == 'GET'):
        search_query = request.GET.get('search', '')    
        #Si se hizo una busqueda de filtrado     
        if search_query:                                      
            instituciones = BusquedaEnCamposQuerySet(instituciones, search_query)                                        
    
    paginator = Paginator(instituciones, 20)  # Mostrar 10 ins por página
    page_number = request.GET.get('page')
    page_insti = paginator.get_page(page_number)

    context = {        
        'page_insti': page_insti,
    }
    return render(request, 'admin/instituciones.html', context)

@login_required
def crearEditarInstitucion(request, pk=None):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    if pk:
        instancia = get_object_or_404(Institucion, pk=pk)
        postUrl = request.build_absolute_uri(reverse('usuarios:AEditarInstitucion', args=[pk]))
        modalTitle = 'Editar Institución'
    else:
        instancia = None
        postUrl = request.build_absolute_uri(reverse('usuarios:ACrearInstitucion'))
        modalTitle = 'Crear Institución'

    if request.method == 'GET':        
        form = InstitucionForm(instance=instancia)
        
    elif request.method == 'POST':        
        form = InstitucionForm(request.POST, instance=instancia)
        if form.is_valid():
            instancia = form.save()            
            messages.success(request, 'Información de institución guardada con éxito')            
            context = {       
                'redirectAfter': request.session['anterior'],
                'modalTitle': modalTitle,
                'mensajes' : 'mensajes.html',
                'postUrl': postUrl,
                'modalForm': form,
            }
            return render(request, 'modal_base.html', context)
        else:
            messages.error(request, form.errors)
    
    context = {    
        'modalTitle': modalTitle,
        'mensajes' : 'mensajes.html',
        'postUrl': postUrl,
        'modalForm': form,
    }
    return render(request, 'modal_base.html', context)

@login_required
def eliminarInstitucion(request, pk):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    institucionBorrar = get_object_or_404(Institucion, pk=pk)    
    institucionBorrar.delete()
    messages.success(request, 'Institución eliminada con éxito')    
    anterior_url = request.session.get('anterior', "usuarios:AInstituciones")
    return redirect(anterior_url)

@login_required
def listaCarreras(request, pkInst):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    institucion = get_object_or_404(Institucion, pk=pkInst)
    CarreraInlineFormSet = inlineformset_factory(Institucion, Carrera, form=CarreraForm, extra=1, exclude=['institucion'])
    postUrl = request.build_absolute_uri(reverse('usuarios:AListaCarreras', args=[pkInst]))
    modalTitle = f'Carreras que pertenecen a <br> {institucion.nombre}'

    if request.method == 'GET':        
        formset = CarreraInlineFormSet(instance=institucion)
    elif request.method == 'POST':
        # Si se envió el formulario, procesa los datos
        formset = CarreraInlineFormSet(request.POST, instance=institucion)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Exito guardando las carreras')            
            return redirect('usuarios:AListaCarreras', pkInst)
        else:
            messages.error(request, formset.errors)
    
    context = {        
        'modalTitle': modalTitle,
        'mensajes' : 'mensajes.html',
        'postUrl': postUrl,
        'modalFormset': formset,
    }
    return render(request, 'modal_base.html', context)


@login_required
def listaUsuarios(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    request.session['anterior'] = request.build_absolute_uri()
    usuarios = Usuario.objects.filter(is_superuser=True)
    solicitantes = Solicitante.objects.all()
    usrNoVerif = User.objects.all().exclude(pk__in=usuarios.values('pk')).exclude(pk__in=solicitantes.values('pk'))

    if (request.method == 'GET'):
        search_query = request.GET.get('search', '')    
        #Si se hizo una busqueda de filtrado     
        if search_query:                                      
            solicitantes = BusquedaEnCamposQuerySet(solicitantes, search_query)
            usuarios = BusquedaEnCamposQuerySet(usuarios, search_query)                             
            usrNoVerif = BusquedaEnCamposQuerySet(usrNoVerif, search_query)    

    paginator = Paginator(usuarios, 10)  # Mostrar 10 usuarios por página
    page_number = request.GET.get('pageA')
    page_admin= paginator.get_page(page_number)
    
    paginator = Paginator(solicitantes, 10)  # Mostrar 10 usuarios por página
    page_number = request.GET.get('pageS')
    page_soli= paginator.get_page(page_number)

    paginator = Paginator(usrNoVerif, 10)  # Mostrar 10 usuarios por página
    page_number = request.GET.get('pageN')
    page_nover= paginator.get_page(page_number)

    context = {
        'page_admin': page_admin,
        'page_soli': page_soli,
        'page_nover': page_nover
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
    if solicitante.municipio:
        estadoSelectForm = EstadoSelectForm(initial={'estado': solicitante.municipio.estado.pk})
    else :
        estadoSelectForm = EstadoSelectForm()
    if solicitante.carrera:
        institucionSelectForm = InstitucionSelectForm(initial={'institucion': solicitante.carrera.institucion.pk})
    else:
        institucionSelectForm = InstitucionSelectForm()
    

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
                messages.success(request, 'Perfil actualizado con éxito')
                return redirect(url)
            else:
                messages.error(request, formPersonal.errors)    

        elif boton == 'domicilio':
            estadoSelectForm = EstadoSelectForm(data = request.POST)   
            formDomicilio = SolicitanteDomicilioForm(request.POST, instance=solicitante) 
            if formDomicilio.is_valid() and estadoSelectForm.is_valid():
                formDomicilio.save()
                messages.success(request, 'Perfil actualizado con éxito')
                return redirect(url)
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
                return redirect(url)
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
def puntajes(request):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    mpForm = PuntajeMunicipioForm()

    if request.method == 'GET':
        formset = PuntajesGeneralesFormSet(queryset=PuntajeGeneral.objects.all())
    elif request.method == 'POST':
        formset = PuntajesGeneralesFormSet(request.POST, queryset=PuntajeGeneral.objects.all())
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Cambios guardados con éxito')
        else:
            messages.warning(request, 'No se pudieron guardar los cambios')
            messages.error(request, formset.errors)

    context = {
        'formset': formset,
        'mpForm': mpForm,
    }
    
    return render(request, 'admin/puntajes.html', context)

def cargar_municipio_puntos(request):
    if request.method == 'GET':  
        estadoId = request.GET.get('estado')    
        municipioId = request.GET.get('municipio')  
    elif request.method == 'POST':  
        estadoId = request.POST.get('estado')    
        municipioId = request.POST.get('municipio')  
    puntaje_municipio = None  # Asigna un valor predeterminado  
    if municipioId:
        municipio = get_object_or_404(Municipio,id=municipioId)  
        try:
            puntaje_municipio = PuntajeMunicipio.objects.get(municipio_id=municipioId)
        except PuntajeMunicipio.DoesNotExist:
            # Si el objeto no existe, créalo
            puntaje_municipio = PuntajeMunicipio(municipio_id=municipioId, puntos=0)  

    if request.method == 'GET':                       
        if municipioId and municipio.estado_id == int(estadoId):               
            mpForm = PuntajeMunicipioForm(instance=puntaje_municipio)            
        else:
            mpForm = PuntajeMunicipioForm()
        mpForm.set_estado(estadoId)
            
    elif request.method == 'POST':      
        mpForm = PuntajeMunicipioForm(request.POST, instance=puntaje_municipio)                 
        mpForm.is_valid()        
        if mpForm.is_valid():
            mpForm.save()
            mpForm.set_estado(estadoId)  
            messages.success(request, 'Puntaje actualizado con éxito.')
        else:
            mpForm.set_estado(estadoId)  
            messages.error(request, mpForm.errors)

    return render(request, 'admin/municipio_puntos.html', {'mpForm': mpForm, 'mensajes': 'mensajes.html'})


@login_required
def eliminarUsuario(request, user_id):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)

    user_to_delete = get_object_or_404(User, pk=user_id)    
    user_to_delete.delete()
    messages.success(request, 'Usuario eliminado con éxito')
    #print('usuario '+ str(user_to_delete) + ' eliminado')    
    anterior_url = request.session.get('anterior', "usuarios:AUsuarios")
    return redirect(anterior_url)

@login_required
def agregarAdmin(request, pk=None):
    usuario = get_object_or_404(Usuario, pk=request.user.id)  
    url = verificarRedirect(usuario, 'permiso_administrador')    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    if pk:
        instancia = get_object_or_404(Usuario, pk=pk)
        postUrl = request.build_absolute_uri(reverse('usuarios:AAgregarAdmin', args=[pk]))
        modalTitle = 'Editar Admin'
    else:
        instancia = None
        postUrl = request.build_absolute_uri(reverse('usuarios:AAgregarAdmin'))
        modalTitle = 'Agregar Admin'

    if request.method == 'GET':        
        form = AgregarAdminForm(instance=instancia)

    if request.method == 'POST':        
        form = AgregarAdminForm(request.POST, instance=instancia)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.is_superuser = True
            instance.is_staff = True
            instancia = form.save()      
            messages.success(request, 'Administrador creado con éxito')            
            context = {       
                'redirectAfter': request.build_absolute_uri(reverse('usuarios:AUsuarios')),
                'mensajes' : 'mensajes.html',
                'postUrl': postUrl,
                'modalForm': form,
            }
            return render(request, 'modal_base.html', context)
        else:
            messages.error(request, form.errors)
    
    context = {     
        'modalTitle': modalTitle,
        'mensajes' : 'mensajes.html',
        'postUrl': postUrl,
        'modalForm': form,
    }
    return render(request, 'modal_base.html', context)