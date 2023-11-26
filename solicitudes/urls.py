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
    path('convocatorias/',views.convocatorias, name='convocatorias'),
    path('convocatorias/<modalidad_id>', views.documentos_convocatorias, name='documentos_convocatoria'),
    path('documento_respuesta/<int:pk>',views.documentoRespuesta, name='documento-respuesta'),
    path('documento/<int:soli>/<int:file>',views.verPDF, name='verPdf'),

    path('administracion/solicitudes', viewsAdmin.solicitudes, name='ASolicitudes'),
]