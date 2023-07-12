"""becas_cozcyt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views, viewsAdmin
from django.urls import path

app_name = 'usuarios'
urlpatterns = [    
    path('login/', views.loginSistema, name='login'),
    path('loginRedirect/', views.loginRedirect, name='loginRedirect'),

    path('primer_login/', views.primerLogin, name='primer_login'),
    path('registrar/', views.register, name='register'),    
    path('cargar_select_municipios/', views.cargar_select_list, 
         kwargs={'app': 'usuarios', 
                 'modDep': 'municipio', 
                 'modIndep': 'estado',
                 'orderBy': 'nombre'}, 
         name='cargar_select_municipios'),  
    path('cargar_select_carreras/', views.cargar_select_list, 
         kwargs={'app': 'usuarios', 
                 'modDep': 'carrera', 
                 'modIndep': 'institucion',
                 'orderBy': 'nombre'}, 
         name='cargar_select_carreras'),  
    path('logout/', views.cerrarSesion, name='logout'),
    path('registrar/confirmar_email/',views.confirmar, name='confirmar'),

    path('perfil/',views.perfil, name='perfil'),
    path('mensajes/',views.sMensajes, name='mensajes'),
    path('convocatorias/',views.convocatorias, name='convocatorias'),
    path('estudioSE/',views.estudioSE, name='estudioSE'),
    path('historial/',views.historial, name='historial'),

    ### urls Administrador ###
    path('administracion/inicio', viewsAdmin.inicio, name='AInicio'),
    path('administracion/solicitudes', viewsAdmin.solicitudes, name='ASolicitudes'),
    path('administracion/estadisticas', viewsAdmin.estadisticas, name='AEstadisticas'),
    path('administracion/usuarios', viewsAdmin.listaUsuarios, name='AUsuarios'),
    path('administracion/configuracion', viewsAdmin.configuracion, name='AConfiguracion'),
    path('administracion/editarUsuario/<int:pk>/', viewsAdmin.editarUsuario, name='AEditarUsuario'),
]