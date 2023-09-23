from django import template
from estudio_socio_economico.models import Elemento
import logging

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