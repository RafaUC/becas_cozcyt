from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Usuario
        fields = ('curp', )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Usuario
        fields = ('curp', )

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
admin.site.register(PuntajeGeneral)
admin.site.register(Solicitante)
admin.site.register(Carrera)
admin.site.register(Institucion)
admin.site.register(Municipio)
admin.site.register(Estado)

