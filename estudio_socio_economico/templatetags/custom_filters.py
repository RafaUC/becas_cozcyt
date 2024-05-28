from django import template
from estudio_socio_economico.models import Elemento
import logging
from django.db import models
from django import forms
from django.utils.timesince import timesince
from django.utils import timezone
from django.templatetags.static import static
import os

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
    

@register.filter(name='elapsed_time')
def elapsed_time(timestamp):
    current_time = timezone.now()
    elapsed_time = current_time - timestamp

    # Calcula los componentes del tiempo transcurrido
    minutes, seconds = divmod(elapsed_time.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days = elapsed_time.days

    # Crea una cadena formateada
    formatted_time = ""
    if days > 0:
        formatted_time += f"{days}d "
    if hours > 0:
        formatted_time += f"{hours}h "
    if minutes > 0:
        formatted_time += f"{minutes}m"

    return formatted_time.strip()
# @register.filter
# def fecha_convocatoria(convocatoria):
#     if (date.today() >= convocatoria.fecha_inicio) and (date.today() <= convocatoria.fecha_cierre):
#         return True
#     else:
#         return False


@register.filter
def static_image(filename):
    base_path, ext = os.path.splitext(filename)
    imageDir = "images"
    
    if ext:
        # Si tiene extensión, verifica si el archivo existe
        path = static(os.path.join(imageDir,filename))
        if os.path.isfile(path):
            return path    
    # Si no tiene extensión, verifica las posibles extensiones
    extensions = ['png', 'svg', 'webp']
    for ext in extensions:
        path = static(os.path.join(imageDir,f'{base_path}.{ext}'))
        if os.path.isfile(path):
            return path
    
    # Retorna un archivo por defecto si no se encuentra el archivo
    return static(os.path.join(imageDir,f'{base_path}.png')) # Default to .png if none found