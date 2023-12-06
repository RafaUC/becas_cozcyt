from django.db import models
from usuarios.models import Solicitante
# Create your models here.

class Notificacion(models.Model):
    TITULO_DEFAULT = 'Departamento de becas COZCYT'

    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)
    titulo = models.CharField(max_length=255, blank=True, null=True, default=TITULO_DEFAULT)
    mensaje = models.TextField()
    redireccion = models.URLField( blank=True, null=True)
    plantilla = models.CharField(max_length=255, default='notificacion.html')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['solicitante', 'timestamp']

    def __str__(self):
        return f'Notificación de {self.solicitante} - {self.timestamp}'