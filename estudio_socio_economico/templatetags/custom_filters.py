from django import template
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