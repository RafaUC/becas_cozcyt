from django.db import models
from usuarios.models import Solicitante
from django.db.models.signals import post_save
from django.dispatch import receiver

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

class Notificacion(models.Model):
    TITULO_DEFAULT = 'Departamento de becas COZCYT'

    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)
    titulo = models.CharField(max_length=255, blank=True, null=True, default=TITULO_DEFAULT)
    mensaje = models.TextField()
    redireccion = models.URLField( blank=True, null=True)
    plantilla = models.CharField(max_length=255, default='notificacion_default.html')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['solicitante', '-timestamp']

    def __str__(self):
        return f'Notificación de {self.solicitante} - {self.timestamp}'

@receiver(post_save, sender=Notificacion)
def notificar_nueva_notificacion(sender, instance, created, **kwargs):        
    if created:
        if instance.solicitante.is_authenticated:
            # Lógica para enviar la notificación al usuario
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{instance.solicitante.id}',
                {
                    'type': 'notificar_notificacion',
                    'mensaje': 'nuevaNotificacion',
                }
            )        