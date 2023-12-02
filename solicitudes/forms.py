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
        fields = ('file',)
        labels = {
            'file' : '',
        }
        exclude = ('solicitud','documento',)
        widgets = {
            # 'file' :  forms.FileField(attrs={'class': 'btn btnSubirDoc',})
        }

class FiltroForm(forms.Form):
    opc = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)
    nombre = None
    search_query_name = ''
    
    def __init__(self, *args,nombre=None, search_query_name='', choices=None, queryset=None, to_field_name=None, initial=None, selectedAll=False, **kwargs):
        super(FiltroForm, self).__init__(*args, **kwargs)        
        if choices:
            self.fields['opc'].choices = choices            
        elif queryset:
            self.fields['opc'].choices = list(queryset.values_list('id', to_field_name))
        if nombre:
            self.nombre = nombre
            self.fields['opc'].label = nombre
        if initial is not None:
            self.fields['opc'].initial = initial
        elif selectedAll:
            self.fields['opc'].initial = [tupla[0] for tupla in self.fields['opc'].choices] 
        self.search_query_name = search_query_name        
    
    def get_search_query(self):            
        if bool(list(self.fields['opc'].choices)):
            self.is_valid()
            selected_options = self.cleaned_data.get('opc', [])    
            st = ''            
            for opc in selected_options:
                st += f'{self.search_query_name}:{opc} '             
            return st
        else:            
            return ''
        