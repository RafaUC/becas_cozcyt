from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'transparencia'
urlpatterns = [
    path('transparencia/', views.inicioTransparencia, name='Tinicio'),
    path('transparencia/resultados/<int:num>', views.resultados, name='Tresultados'),
    path('transparencia/resultados/<int:num>/<int:mod>', views.resultadosContenido, name='TresCont'),
    path('transparencia/sit', views.transparenciaSIT, name='Tsit'),    
    path('transparencia/sitInfo', views.transparenciaSITInfo, name='TsitInfo'),
]