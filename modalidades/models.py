from django.db import models
import os
from uuid import uuid4
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from datetime import date


def ciclo_actual(offset=0):
    now = datetime.now()
    mes = (now.month + offset) % 12
    año = now.year + ((now.month + offset) // 12)
    # Determinar el ciclo actual
    if mes >= 8:
        ciclo = "Agosto - Diciembre"
    else:
        ciclo = "Enero - Junio"    
    return f"{ciclo} {año}"

def obtener_mes_numero(mes):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return meses.index(mes) + 1

def ordenar_lista_ciclos(registros):
    return sorted(registros, key=lambda x: (int(x.split()[-1]), obtener_mes_numero(x.split()[0])))



def modalidadMediaPath(instance, filename):
    ext = filename.split('.')[-1]  # Obtiene la extensión del archivo
    filename = f"{uuid4().hex}.{ext}"  # Genera un nombre único utilizando UUID
    return os.path.join('media/', filename)  # Ruta de almacenamiento deseada

class Convocatoria(models.Model):
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_cierre = models.DateField(null=False, blank=False)
    presupuesto = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return f'Convocatoria {self.fecha_inicio} // {self.fecha_cierre}' #date.today()

    @property
    def mostrar_precio(self):
        return "%s" % self.presupuesto        
    
    @property
    def fecha_convocatoria(self):
        if (date.today() >= self.fecha_inicio) and (date.today() <= self.fecha_cierre):
            return True
        else:
            return False
        
    @property
    def mensaje_estado_convocatoria(self):        
        if date.today() == self.fecha_cierre:
            return f'Último día de convocatoria.'
        elif date.today() < self.fecha_inicio:
            dias_restantes = (self.fecha_inicio - date.today()).days
            if dias_restantes < 2:
                return f'Falta {dias_restantes} día para que inicie la convocatoria.'
            else:
                return f'Faltan {dias_restantes} días para que inicie la convocatoria.'
        elif date.today() <= self.fecha_cierre:
            dias_restantes = (self.fecha_cierre - date.today()).days+1
            if dias_restantes < 2:
                return f'Queda {dias_restantes} día para que la convocatoria termine.'
            else:
                return f'Quedan {dias_restantes} días para que la convocatoria termine.'
        else:
            return 'La convocatoria ha terminado.'

class Modalidad(models.Model):
    TIPO_CHOICES = [
        ('Renovacion', 'Renovación'),
        ('Ingreso', 'Nuevo Ingreso')
    ]
    nombre = models.CharField(max_length=255, verbose_name="Nombre", null=False)
    imagen = models.ImageField(upload_to=modalidadMediaPath, verbose_name="Imagen", null=False)
    descripcion = models.TextField(verbose_name="Descripción", null=False)
    monto = models.DecimalField(max_digits=7, decimal_places=2,verbose_name="monto", null=True)
    mostrar = models.BooleanField(default=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_CHOICES[1][0])

    def __str__(self):
        return f'{self.nombre} ({self.tipo})'
    
    def get_documentos_children(self):
        return self.documento_set.all()
    
    class Meta:        
        ordering = ['nombre','tipo']
    
class Documento(models.Model):
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, verbose_name=_("Modalidad"), null=False)
    nombre = models.CharField(max_length=255, verbose_name=_("Nombre"), null=False)
    descripcion = models.CharField(max_length=255, verbose_name=_("Descripción"), null=False)
    order = models.IntegerField(verbose_name='orden', default=0)

    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")
        ordering = ['order','id']

    def __str__(self):
        return self.nombre
    
    def get_queryset(self):
        return super().get_queryset().filter(nombre="Curp")