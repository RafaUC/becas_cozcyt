from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class SolicitanteAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('curp', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'ap_paterno', 'ap_materno', 'fecha_nacimiento', 'genero', 'g_etnico')}),
        ('Información de Contacto', {'fields': ('email', 'tel_cel', 'tel_fijo', 'municipio', 'colonia', 'calle', 'numero', 'codigo_postal')}),
        ('Información Adicional', {'fields': ('folio', 'rfc', 'grado', 'promedio', 'carrera')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'email_verified_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('curp', 'password1', 'password2'),
        }),
        ('Información Personal', {'fields': ('nombre', 'ap_paterno', 'ap_materno', 'fecha_nacimiento', 'genero', 'g_etnico')}),
        ('Información de Contacto', {'fields': ('email', 'tel_cel', 'tel_fijo', 'municipio', 'colonia', 'calle', 'numero', 'codigo_postal')}),
        ('Información Adicional', {'fields': ('folio', 'rfc', 'grado', 'promedio', 'carrera')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    list_display = ('curp', 'nombre', 'ap_paterno', 'ap_materno', 'folio', 'email', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('curp', 'nombre', 'ap_paterno', 'ap_materno', 'email')
    ordering = ('-is_superuser', 'id')

class UsuarioAdmin(UserAdmin):

    add_fieldsets = (
        (None, {'fields': ('curp', 'password1', 'password2')}),
        ('Información personal', {'fields': ('nombre', 'email')}),
        ('Permisos', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Login info', {'fields': ('last_login',)}),
    ) 
    # Campos que se mostrarán en el formulario de usuario en el sitio de administración
    fieldsets = (
        (None, {'fields': ('curp', 'password')}),
        ('Información personal', {'fields': ('nombre', 'email')}),
        ('Permisos', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Login info', {'fields': ('last_login',)}),
    )
    # Campos que se mostrarán en la lista de usuarios en el sitio de administración
    list_display = ('curp', 'nombre', 'email', 'is_staff', 'is_superuser')
    # Campos por los que se puede buscar en la lista de usuarios en el sitio de administración
    search_fields = ('curp', 'nombre', 'email')
    # Muestra el campo de contraseña como un campo de contraseña enmascarado
    #readonly_fields = ('password',)
    # Eliminar la configuración de ordering
    ordering = ['curp']

    list_filter = ('is_staff', 'is_superuser')

# Registrar el modelo Usuario con la clase UsuarioAdmin personalizada
admin.site.register(Usuario, UsuarioAdmin)

#admin.site.register(Usuario)
admin.site.register(PuntajeMunicipio)
admin.site.register(PuntajeGeneral)
admin.site.register(Solicitante, SolicitanteAdmin)
admin.site.register(Carrera)
admin.site.register(Institucion)
admin.site.register(Municipio)
admin.site.register(Estado)

