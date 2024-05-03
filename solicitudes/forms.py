from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.db.models import Subquery

from .models import *
from modalidades.models import ordenar_lista_ciclos

# class ConvocatoriaForm(ModelForm):


class SolicitudForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SolicitudForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = Solicitud
        exclude = ('modalidad', 'solicitante',)
        
class DocumentoRespForm(ModelForm):
    file = forms.FileField(required=False ,widget=forms.FileInput(attrs={'class': 'pdfInput', 'accept': '.pdf', 'hidden': True}))
    class Meta:
        model = RespuestaDocumento
        fields = ['file']        

        labels = {
            'file': 'Archivo',
        }
    def clean_file(self):        
        r = self.cleaned_data.get('file')        
        if not r :
            raise forms.ValidationError("Este campo es Obligatorio.")
        return r

class FiltroForm(forms.Form):
    opc = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=False)
    nombre = None
    search_query_name = ''
    
    def __init__(self, *args,nombre=None, search_query_name='', choices=None, queryset=None, to_field_name=None, initial=None, selectedAll=False, **kwargs):
        super(FiltroForm, self).__init__(*args, **kwargs)        
        if choices:
            self.fields['opc'].choices = choices            
        elif queryset:
            if to_field_name == '__str__':
                self.fields['opc'].choices = [(obj.id, str(obj)) for obj in queryset]
            else:
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
        
    
class EstadisticaSelectForm(forms.Form):
     # Campo para los valores únicos de un campo específico
    estadistica_filtro = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'EstadInfoSelect border-1 form-select form-select-sm'}))
    # Campo para los nombres de los campos del modelo
    campo_estadistica = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'EstadInfoSelect border-1 form-select form-select-sm'}))

    def __init__(self, *args, **kwargs):
        filtro_label = kwargs.pop('filtro_label', None)
        filtro_choices = kwargs.pop('filtro_choices', None)
        campo_label = kwargs.pop('campo_label', None)
        campo_choices = kwargs.pop('campo_choices', None)
        super().__init__(*args, **kwargs)

        if filtro_label:
            self.fields['estadistica_filtro'].label = filtro_label
        if filtro_choices:
            self.fields['estadistica_filtro'].choices = filtro_choices
        if campo_label :
            self.fields['campo_estadistica'].label = campo_label
        if campo_choices: 
            self.fields['campo_estadistica'].choices = campo_choices


class EstadInfoSelectForm(forms.Form):
    # Campo para los valores únicos de un campo específico
    estadistica_filtro = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'EstadInfoSelect border-1 form-select form-select-sm'}))

    # Campo para los nombres de los campos del modelo
    campo_estadistica = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'EstadInfoSelect border-1 form-select form-select-sm'}))

    def __init__(self, *args, **kwargs):
        modelo_filtro = kwargs.pop('modelo_filtro', None)
        campo_filtro = kwargs.pop('campo_filtro', None)
        campo_estadistica_modelo = kwargs.pop('campo_estadistica_modelo', None)
        extra_choices = kwargs.pop('extra_choices', None)
        exclude_choices = kwargs.pop('exclude_choices', None)
        super().__init__(*args, **kwargs)

        if modelo_filtro and campo_filtro and campo_estadistica_modelo:
            #Generar las choices del estadistica_filtro
            if campo_filtro == 'ciclo' and modelo_filtro == Solicitud:
                valores_unicos = modelo_filtro.objects.all().order_by().values_list('ciclo', flat=True).distinct()
                valores_unicos = ordenar_lista_ciclos(valores_unicos)
                valores_unicos.reverse()
            else:
                # Obtener los valores únicos basados en los parámetros de la consulta GET
                valores = modelo_filtro.objects.all().values_list(campo_filtro, flat=True)
                valores_unicos = []
                conjunto_vistos = set()
                for elemento in valores:
                    if elemento not in conjunto_vistos:
                        valores_unicos.append(elemento)
                        conjunto_vistos.add(elemento)
            self.fields['estadistica_filtro'].choices = [(valor, valor) for valor in valores_unicos]
            self.fields['estadistica_filtro'].choices.insert(0, ('Todos', 'Todos'))
            self.fields['estadistica_filtro'].label = campo_filtro

            # Rellenar el campo campos_modelo con los nombres de los campos del modelo
            campos = [campo for campo in campo_estadistica_modelo._meta.get_fields() if
                      isinstance(campo, models.Field) and campo.name != 'id']
            self.fields['campo_estadistica'].choices = [(campo.name, campo.name) for campo in campos]
            if exclude_choices:
                self.fields['campo_estadistica'].choices = [choice for choice in self.fields['campo_estadistica'].choices if (choice[0] not in exclude_choices) or (choice[1] not in exclude_choices)]            
            if extra_choices:
                for choice in extra_choices:
                    self.fields['campo_estadistica'].choices.append(choice)
            self.fields['campo_estadistica'].label = 'Atributo'