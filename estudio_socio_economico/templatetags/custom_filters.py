from django import template
from estudio_socio_economico.models import Elemento
import logging
from django.db import models
from django import forms
from datetime import datetime
from datetime import date

register = template.Library()
logger = logging.getLogger(__name__)

@register.filter
def hashD(d, key):        
    try:                        
        return d[key]
    except Exception as e:
        #logger.exception("Ocurrió una excepción al usar filtro: %s", str(e))        
        return None

@register.filter
def enlistarRows(elementos):        
    rows = []
    row = []
    ultimoRow = None
    for elemento in elementos:
        if elemento.row != ultimoRow and ultimoRow is not None:
            rows.append(row)
            row = []
        row.append(elemento)        
        ultimoRow = elemento.row
    return rows

    

@register.filter
def splitPop(s,str):    
    try:        
        return (s.split(str).pop())
    except Exception as e:
        #logger.exception("Ocurrió una excepción al usar filtro: %s", str(e))
        return None
    
@register.filter(name='is_list')
def is_list(value):
    return isinstance(value, list)

@register.filter
def model_verbose_name(obj):    
    #Devuelve el 'verbose name' del modelo asociado a un formulario o un formset.    
    try:
        # Intenta obtener el 'verbose name' del modelo
        if isinstance(obj, models.Model):
            return obj.model._meta.verbose_name
        elif isinstance(obj, forms.BaseForm):
            return obj.Meta.model._meta.verbose_name
    except Exception as e:
        print(e)
        return ' '
    
# @register.filter
# def fecha_convocatoria(convocatoria):
#     if (date.today() >= convocatoria.fecha_inicio) and (date.today() <= convocatoria.fecha_cierre):
#         return True
#     else:
#         return False