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

app_name = 'estudioSE'
urlpatterns = [
    path('administracion/config/estudio', viewsAdmin.configEstudio, name='AConfigEstudio'),
    path('administracion/config/getStudioForm', viewsAdmin.configEstudioGetForm, name='AConfigGetEstudioForm'),
    path('estudioSE/',views.estudioSE, name='estudioSE'),
    path('agregarRegistroSE/<int:seccionID>/',views.agregarR, name='AgregarR'),
    path('eliminarRegistroSE/<int:seccionID>/<int:registroID>/',views.eliminarR, name='EliminarR'),
    path('estudioSE/descargarPDF/',views.getEstudioPDF, name='estudioSE_PDF'),
]