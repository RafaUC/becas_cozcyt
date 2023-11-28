from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from .models import *

class SolicitudForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SolicitudForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Solicitud
        exclude = ('modalidad', 'solicitante',)
        # fields = ('modalidad','solicitante',)
        # labels = {
        #    'modalidad' : '',
        #    'solicitante' : '',
        # }
        # widgets = {
        #     'modalidad' : forms.TextInput(attrs={'class': 'form-control'})
        # }
class DocumentoRespForm(ModelForm):
    file = forms.FileField()
    file.widget.attrs.update({'id': 'file-upload'})
    class Meta:
        model = RespuestaDocumento
        # fields = ('file',)
        fields = '__all__'
        labels = {
            'file' : '',
        }
        # exclude = ('solicitud','documento',)
        widgets = {
            # 'file' :  forms.FileField(attrs={'class': 'btn btnSubirDoc',})
        }
        