from django import forms
from .models import Seccion, Opcion, Elemento
from django.forms import inlineformset_factory, modelformset_factory
from .models import RNumerico, RTextoCorto, RTextoParrafo, RHora, RFecha, ROpcionMultiple, RCasillas, RDesplegable, Respuesta
from django.core.validators import MinLengthValidator, MaxLengthValidator


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'tipo', 'orden']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-lg font-semi-bold border-3'}),
            'tipo': forms.RadioSelect(attrs={'class': 'form-check-input checkbox-principal'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'type': 'hidden'}),
        }
        labels = {
            'nombre': 'Nombre de la Sección',
            'tipo': 'Tipo de la Sección',
            'orden': 'orden',
        }
        
        

class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ['elemento', 'nombre', 'orden']
        widgets = {
            'elemento': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'opcion-text form-control border-3 p-0 m-0', 'onkeyup': 'updateOpcionInputSize(this)', 'onkeydown': 'updateOpcionInputSize(this)', 'oninput': 'detectarTerminarEscritura(this)'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'type': 'hidden'}),
        }
        labels = {
            'elemento': 'Elemento',
            'nombre': 'Nombre Opción',
            'orden': 'orden',
        }
        
        

class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = ['seccion', 'nombre', 'obligatorio', 'opcionOtro', 'numMin', 'numMax', 'row', 'col', 'tipo',]
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-control form-control-sm border-3', 'placeholder': 'Selecciona una sección'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm font-semi-bold border-3 ', 'placeholder': 'Nombre de la pregunta'}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'checkbox-principal form-check-input'}),            
            'opcionOtro': forms.CheckboxInput(attrs={'class': 'checkbox-principal form-check-input', 'title': 'Habilitar Opción Otro', 'data-bs-original-title': 'Habilitar Opción Otro'}),            
            'numMin': forms.NumberInput(attrs={'class': 'opcion-digit form-control form-control-sm border-3' }),
            'numMax': forms.NumberInput(attrs={'class': 'opcion-digit form-control form-control-sm border-3' }),
            'row': forms.NumberInput(attrs={'class': 'form-control form-control-sm border-3', 'type': 'hidden'}),
            'col': forms.NumberInput(attrs={'class': 'form-control form-control-sm border-3', 'type': 'hidden'}),
            'tipo': forms.Select(attrs={'class': 'form-select form-select-sm border-3 elem-tipo-select', 'onchange': 'toggleElementoOpciones(this)', 'onload': 'toggleElementoOpciones(this)', 'placeholder': 'Tipo de pregunta'}),
        }
        labels = {
            'seccion': 'Sección',
            'nombre': 'Nombre de la Pregunta',
            'obligatorio': 'Obligatorio',        
            'opcionOtro': 'Opc. Otro',
            'numMin': 'Min. Dígitos', 
            'numMax': 'Max. Dígitos',
            'row': 'row',
            'col': 'col',
            'tipo': 'Tipo de Pregunta',            
        }
        
SeccionFormSet = modelformset_factory(Seccion, form=SeccionForm, extra=1, can_delete=True)
ElementoFormSet = inlineformset_factory(Seccion, Elemento, form=ElementoForm, extra=1, can_delete=True)
OpcionFormSet = inlineformset_factory(Elemento, Opcion, form=OpcionForm, extra=1, can_delete=True)

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = []

    def __init__(self, *args, **kwargs):
        elemento = kwargs.pop("elemento", None)
        solicitante = kwargs.pop("solicitante", None)
        super(RespuestaForm, self).__init__(*args, **kwargs)
        if elemento and solicitante:
            self.instance.solicitante = solicitante
            self.instance.elemento = elemento        

        if self.instance and hasattr(self.instance, 'elemento') and self.fields:
            elemento_nombre = self.instance.elemento.nombre
            first_field_name = list(self.fields.keys())[0]
            self.fields[first_field_name].widget.attrs['placeholder'] = elemento_nombre
    
    """def add_prefix(self, field_name):
        field_name = super(RespuestaForm, self).add_prefix(field_name)
        return self.prefix """


class RNumericoForm(RespuestaForm):
    class Meta:
        model = RNumerico
        fields = ['valor']
        widgets = {'valor': forms.TextInput(attrs={'class': 'form-control border-3', 'onkeypress': "return isNumberPuntKey(event)"}),}
        labels = {'valor': 'Respuesta numérica'}

    def __init__(self, *args, **kwargs):
        super(RNumericoForm, self).__init__(*args, **kwargs)

        # Accede a la instancia de elemento y obtén los valores numMin y numMax
        elemento = self.instance.elemento if self.instance else None
        numMin = elemento.numMin if elemento else None
        numMax = elemento.numMax if elemento else None

        # Configura validadores de longitud mínima y máxima en el campo 'valor'
        if numMin is not None:
            self.fields['valor'].validators.append(MinLengthValidator(numMin))
            self.fields['valor'].widget.attrs['minlength'] = numMin
        if numMax is not None:
            self.fields['valor'].validators.append(MaxLengthValidator(numMax))
            self.fields['valor'].widget.attrs['maxlength'] = numMax


    def clean_valor(self):
        obligatorio = self.instance.elemento.obligatorio    
        r = self.cleaned_data.get('valor')
        if (not r or not r.strip()) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")
        return r
    

class RTextoCortoForm(RespuestaForm):
    class Meta:
        model = RTextoCorto
        fields = ['texto']
        widgets = {'texto': forms.TextInput(attrs={'class': 'form-control border-3'}),}
        labels = {'texto': 'Respuesta texto corto'}

    def clean_texto(self):
        obligatorio = self.instance.elemento.obligatorio    
        r = self.cleaned_data.get('texto')
        if (not r or not r.strip()) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")
        return r


class RTextoParrafoForm(RespuestaForm):
    class Meta:
        model = RTextoParrafo
        fields = ['texto']
        widgets = {'texto': forms.Textarea(attrs={'class': 'form-control border-3'}),}
        labels = {'texto': 'Respuesta párrafo'}

    def clean_texto(self):
        obligatorio = self.instance.elemento.obligatorio    
        r = self.cleaned_data.get('texto')
        if (not r or not r.strip()) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")
        return r


class RHoraForm(RespuestaForm):
    class Meta:
        model = RHora
        fields = ['hora']
        widgets = {'hora': forms.TimeInput(attrs={'class': 'form-control border-3', 'type': 'time'}),}
        labels = {'hora': 'Hora'}

    def clean_hora(self):
        obligatorio = self.instance.elemento.obligatorio    
        r = self.cleaned_data.get('hora')
        if (not r) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")
        return r


class RFechaForm(RespuestaForm):
    class Meta:
        model = RFecha
        fields = ['fecha']
        widgets = {'fecha': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control border-3', 'type': 'date'}),}
        labels = {'fecha': 'Fecha'}

    def clean_fecha(self):
        obligatorio = self.instance.elemento.obligatorio    
        r = self.cleaned_data.get('fecha')
        if (not r) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")
        return r
   

class ROpcionMultipleForm(RespuestaForm):
    class Meta:
        model = ROpcionMultiple
        fields = ['respuesta', 'otro']
        widgets = {'respuesta': forms.RadioSelect(attrs={'class': 'form-check-input checkbox-principal', 'onchange': 'toggleOtroCampo(this)'}),
                   'otro': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Otro'}),}
        labels = {'respuesta': 'Respuesta de opción múltiple', 'otro': 'Otro'}

    def clean(self):
        cleaned_data = super().clean()           
        obligatorio = self.instance.elemento.obligatorio  
        opcOtro = self.instance.elemento.opcionOtro     
        respuesta = cleaned_data.get('respuesta')        
        otro = cleaned_data.get('otro')                  
        if obligatorio:
            if not ((opcOtro and (otro and otro.strip())) or not opcOtro) and (respuesta and respuesta.nombre == 'Otro'):
                raise forms.ValidationError("Este campo es obligatorio")
        if (otro and otro.strip()) and (respuesta and not respuesta.nombre == 'Otro'):
            raise forms.ValidationError("No esta seleccionada opcion Otro")        
        if respuesta and (respuesta.nombre == 'Otro' and not( otro and otro.strip())):
            raise forms.ValidationError("Si eliges 'otro', debes proporcionar más detalles en el campo 'otro'.")      
        return cleaned_data


    def clean_respuesta(self):        
        respuesta = self.cleaned_data.get('respuesta')                          
        obligatorio = self.instance.elemento.obligatorio  
        if (not respuesta) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")        
        return respuesta

    
class RCasillasForm(RespuestaForm):
    class Meta:
        model = RCasillas
        fields = ['respuesta', 'otro']
        widgets = {'respuesta': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input checkbox-principal form-check-inline-custom', 'style': 'display: inline-block;', 'onchange': 'toggleOtroCampo(this)'}),
                   'otro': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Otro'}),}
        labels = {'respuestas': 'Casillas', 'otro': 'Otro'}

    def clean(self):
        cleaned_data = super().clean()           
        obligatorio = self.instance.elemento.obligatorio  
        opcOtro = self.instance.elemento.opcionOtro     
        respuesta = cleaned_data.get('respuesta')              
        otro = cleaned_data.get('otro')                  
        if obligatorio:
            if not ((opcOtro and (otro and otro.strip())) or not opcOtro) and (respuesta and respuesta.filter(nombre='Otro').exists()):
                raise forms.ValidationError("Este campo es obligatorio")
        if (otro and otro.strip()) and (respuesta and not respuesta.filter(nombre='Otro').exists()):
            raise forms.ValidationError("No esta seleccionada opcion Otro")        
        if respuesta and (respuesta.filter(nombre='Otro').exists() and not( otro and otro.strip())):
            raise forms.ValidationError("Si eliges 'otro', debes proporcionar más detalles en el campo 'otro'.")      
        return cleaned_data

    def clean_respuesta(self):
        respuesta = self.cleaned_data.get('respuesta')        
        noRespuesta = respuesta.count() == 0              
        obligatorio = self.instance.elemento.obligatorio  
        if (noRespuesta) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")    
        return respuesta


class RDesplegableForm(RespuestaForm):
    class Meta:
        model = RDesplegable
        fields = ['respuesta', 'otro']
        widgets = {'respuesta': forms.Select(attrs={'class': 'form-control form-select border-3', 'onchange': 'toggleOtroCampo(this)'}),
                   'otro': forms.TextInput(attrs={'class': 'form-control border-3', 'placeholder': 'Otro'}),}
        labels = {'respuesta': 'Respuesta de desplegable', 'otro': 'Otro'}
    
    def clean(self):
        cleaned_data = super().clean()           
        obligatorio = self.instance.elemento.obligatorio  
        opcOtro = self.instance.elemento.opcionOtro     
        respuesta = cleaned_data.get('respuesta')        
        otro = cleaned_data.get('otro')                  
        if obligatorio:
            if not ((opcOtro and (otro and otro.strip())) or not opcOtro) and (respuesta and respuesta.nombre == 'Otro'):
                raise forms.ValidationError("Este campo es obligatorio")
        if (otro and otro.strip()) and (respuesta and not respuesta.nombre == 'Otro'):
            raise forms.ValidationError("No esta seleccionada opcion Otro")        
        if respuesta and (respuesta.nombre == 'Otro' and not( otro and otro.strip())):
            raise forms.ValidationError("Si eliges 'otro', debes proporcionar más detalles en el campo 'otro'.")      
        return cleaned_data


    def clean_respuesta(self):        
        respuesta = self.cleaned_data.get('respuesta')                          
        obligatorio = self.instance.elemento.obligatorio  
        if (not respuesta) and obligatorio:
            raise forms.ValidationError("Este campo es Obligatorio.")        
        return respuesta
