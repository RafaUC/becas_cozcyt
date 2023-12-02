from django.db import models
import os
from uuid import uuid4
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime


def ciclo_actual():
        now = datetime.now()
        mes = now.month
        # Determinar el ciclo actual
        if mes >= 8:
            ciclo = "Agosto - Diciembre"
        else:
            ciclo = "Enero - Junio"
        # Obtener el año actual
        año = now.year
        return f"{ciclo} {año}"

def modalidadMediaPath(instance, filename):
    ext = filename.split('.')[-1]  # Obtiene la extensión del archivo
    filename = f"{uuid4().hex}.{ext}"  # Genera un nombre único utilizando UUID
    return os.path.join('media/', filename)  # Ruta de almacenamiento deseada


class Modalidad(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre", null=False)
    imagen = models.ImageField(upload_to=modalidadMediaPath, verbose_name="Imagen", null=False)
    descripcion = models.TextField(verbose_name="Descripción", null=False)

    def __str__(self):
        return self.nombre
    
    def get_documentos_children(self):
        return self.documento_set.all()
    
class Documento(models.Model):
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, verbose_name=_("Modalidad"), null=False)
    nombre = models.CharField(max_length=255, verbose_name=_("Nombre"), null=False)
    descripcion = models.CharField(max_length=255, verbose_name=_("Descripción"), null=False)
    order = models.IntegerField(verbose_name='orden', default=100_000)

    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")
        ordering = ['order']

    def __str__(self):
        return self.nombre
    
    def get_queryset(self):
        return super().get_queryset().filter(nombre="Curp")