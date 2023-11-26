from django.db import models
from usuarios.models import Solicitante
from modalidades.models import Modalidad, Documento, ciclo_actual
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from uuid import uuid4
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('docPendiente', 'Documentación pendiente'),
        ('docAprobada', 'Documentación aprobada'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]

    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, null=False)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE, null=False)
    ciclo = models.CharField(max_length=50, default=ciclo_actual(), editable=False, null=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    readonly_fields = ('ciclo',)
    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        unique_together = ('modalidad', 'solicitante')


def validador_pdf(value):
    ext = os.path.splitext(value.name)[1]  # Obtener la extensión del archivo
    valid_extensions = ['.pdf']  # Lista de extensiones permitidas
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Sólo se permiten archivos en formato PDF.'))

def documentoMediaPath(instance, filename):
    ext = filename.split('.')[-1]  # Obtiene la extensión del archivo
    filename = f"{uuid4().hex}.{ext}"  # Genera un nombre único utilizando UUID
    return os.path.join("protected_uploads/", filename)  #Obtener la ruta de la carpeta que se va a crear por solicitud


class RespuestaDocumento(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('denegado', 'Denegado'),
    ]
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    file = models.FileField(upload_to=documentoMediaPath, validators=[validador_pdf])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"DocRespuesta: s:{self.solicitud_id} - {self.id} {self.documento} - {self.estado}"

    class Meta:
        verbose_name = 'Documento de Respuesta'
        verbose_name_plural = 'Documentos de Respuesta'
        unique_together = ('solicitud', 'documento')

#Signal que despues guardar algun RespuestaDocumento verifica que la solicitud a la que pertenece
#cumple con las condiciones para pasar a estado docAprobada o no
@receiver(post_save, sender=RespuestaDocumento)
def actualizar_estado_solicitud(sender, instance, **kwargs):
    # Verificar condiciones y actualizar estado de la solicitud        
    aprobado = False
    solicitud = instance.solicitud
    if instance.estado == RespuestaDocumento.ESTADO_CHOICES[1][0]: #'aprobado'        
        # Verificar que existan todas las instancias necesarias de RespuestaDocumento
        documentos_modalidad = solicitud.modalidad.documento_set.all()
        respuestas_documentos_solicitud = RespuestaDocumento.objects.filter(solicitud=solicitud)                
        if set(documentos_modalidad) == set({resp.documento for resp in respuestas_documentos_solicitud}):
            # Todas las instancias necesarias de RespuestaDocumento existen

            # Verificar que todas las instancias de RespuestaDocumento de la solicitud estén aprobadas            
            if respuestas_documentos_solicitud.filter(estado='aprobado').count() == respuestas_documentos_solicitud.count():
                # Todas las instancias de RespuestaDocumento de la solicitud están aprobadas
                aprobado = True        
    if aprobado:
        solicitud.estado = Solicitud.ESTADO_CHOICES[1][0] #'docAprobada'
    else:
        solicitud.estado = Solicitud.ESTADO_CHOICES[0][0] #'docPendiente'

    solicitud.save()