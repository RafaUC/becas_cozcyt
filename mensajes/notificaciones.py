from .models import Notificacion
from django.urls import reverse

# importar como: form mensajes import notificaciones as notif

"""
 Ejemplos:
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    notif.nueva(solicitante, 'Mi mensaje', 'usuarios:perfil')

    notif.nueva(solicitante, titulo='MI TITULO', mensaje='Mi mensaje', url='solicitudes:convocatoria', urlArgs=[id])
"""

# solicitante: Solicitante al que se le mostrara la notificacion
# mensaje: Mansaje de la notificacion
# url: url con patron de django a la cual rediccionara al dar click a la notificacion, Tambien se puede dar nunguna url
# urlArgs: Argumentos de la url en caso de que la vista y url los necesite
# titulo: Titulo de la notificacion
# plantilla: Plantilla con el que se renderizara el div de la notificacion
def nueva(solicitante, mensaje, url=None, urlArgs=None, titulo=Notificacion.TITULO_DEFAULT, plantilla='notificacion_default.html'):
    
    if url:
        url_invertida = reverse(url, args=urlArgs)
    else:
        url_invertida = '#'

    return Notificacion.objects.create(solicitante=solicitante, titulo=titulo, mensaje=mensaje, redireccion=url_invertida, plantilla=plantilla)

