from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'transparencia'
urlpatterns = [
    path('transparencia/', views.inicioTransparencia, name='Tinicio'),
    path('transparencia/beneficiarios/<int:num>', views.resultados, name='TBeneficiarios'),
    path('transparencia/beneficiarios/<int:num>/<int:mod>', views.resultadosContenido, name='TresCont'),
    path('transparencia/sit', views.transparenciaSIT, name='Tsit'),    
    path('transparencia/sitInfo', views.transparenciaSITInfo, name='TsitInfo'),
]