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

app_name = 'solicitudes'
urlpatterns = [
    path('convocatoria/',views.convocatorias, name='convocatorias'),
    path('convocatoria/<modalidad_id>', views.documentos_convocatorias, name='documentos_convocatoria'),
    path('documento_respuesta/<int:pk>',views.documentoRespuesta, name='documento-respuesta'),
    path('documento/<int:soli>/<int:file>',views.verPDF, name='verPdf'),
    path('historial/',views.historial, name='historial'),
    path('convocatoria/documentacion/<modalidad_id>', views.documentos_convocatorias, name='documentos_convocatoria'),

    path('administracion/solicitudes', viewsAdmin.listaSolicitudes, name='ASolicitudes'),
    path('historialSolicitante/<int:pk>',viewsAdmin.historialSolicitante, name='AHistorial'),
    path('documentosSolicitante/<int:pk>', viewsAdmin.documentos_solicitante, name="ADocumentos"),    
    path('administracion/concentrado/solicitud/<int:pk>', viewsAdmin.concentradoSolicitud, name='AConcentradoSoli'),
    path('administracion/concentrado/convocatoria/<str:ciclo>', viewsAdmin.concentradoConvocatoria, name='AConcentradoConv'),

    path('administracion/estadisticas', viewsAdmin.estadisticas, name='AEstadisticas'),
    path('administracion/estadisticas/solicitudes', viewsAdmin.estadisticaSolicitudes, name='ESolicitudes'),
]