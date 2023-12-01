from django.db import models
from usuarios.models import Solicitante
from modalidades.models import Modalidad, Documento, ciclo_actual
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from uuid import uuid4
import os
# Create your models here.


class Solicitud(models.Model):
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, null=False)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE, null=False)
    ciclo = models.CharField(max_length=50, default=ciclo_actual(), editable=False, null=False)

    readonly_fields = ('ciclo',)
    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        unique_together = ('modalidad', 'solicitante')

    def __str__(self):
        return f'{self.modalidad}/  {self.solicitante}/  {self.ciclo}'


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
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    file = models.FileField(upload_to=documentoMediaPath, validators=[validador_pdf])

    class Meta:
        verbose_name = 'Documento de Respuesta'
        verbose_name_plural = 'Documentos de Respuesta'
        unique_together = ('solicitud', 'documento')

    def __str__(self):
        return f'{self.solicitud}/ {self.documento}'
    
    @property
    def filename(self) -> str:
        return os.path.basename(self.file.name)
        