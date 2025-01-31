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
from django.urls import path
from . import views, viewsAdmin

app_name = 'modalidades'
urlpatterns = [
    path('administracion/configuracion/modalidades', viewsAdmin.configModalidades, name = 'AConfigModalidades'),
    path('administracion/configuracion/modalidades/mostrar_mod/<modalidad_id>', viewsAdmin.mostrar_modalidad, name="mostrar_modalidad"),
    path('administracion/configuracion/modalidades/agregar_modalidad', viewsAdmin.agregarModalidad, name = 'AConfigAgregarModalidad'),
    path('eliminar_modalidad/<modalidad_id>', viewsAdmin.eliminarModalidad, name = 'AConfigEliminarModalidades'),
    path('archivar_modalidad/<modalidad_id>', viewsAdmin.archivarModalidad, name = 'AConfigArchivarModalidades'),
    path('editar_modalidad/<modalidad_id>', viewsAdmin.editarModalidad, name = 'AConfigEditarModalidades'),
    path('eliminar_documento/<modalidad_id>/<documento_id>', viewsAdmin.eliminarDocumento, name = 'AConfigEliminarDocumento'),
    
    path('administracion/configuracion/general', viewsAdmin.configGeneral, name = 'AConfigGeneral'),
    path('administracion/configuracion/publicarResultados', viewsAdmin.togglePublicarUltimosResultados, name = 'APublicRes'),
]

htmx_urlpatterns = [
    # path('ordenar/', viewsAdmin.ordenarDocumentos, name="OrdenarDocumentos"),
]

urlpatterns += htmx_urlpatterns