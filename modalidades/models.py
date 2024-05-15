from django.db import models
import os
from uuid import uuid4
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from datetime import date
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


'''
def obtener_mes_numero(mes):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    return meses.index(mes) + 1

def ordenar_lista_ciclos(registros):
    return sorted(registros, key=lambda x: (int(x.split()[-1]), obtener_mes_numero(x.split()[0])))
'''
    
def validador_pdf(value):
    ext = os.path.splitext(value.name)[1]  # Obtener la extensión del archivo
    valid_extensions = ['.pdf']  # Lista de extensiones permitidas
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Sólo se permiten archivos en formato PDF.'))

def modalidadMediaPath(instance, filename):
    ext = filename.split('.')[-1]  # Obtiene la extensión del archivo
    filename = f"{uuid4().hex}.{ext}"  # Genera un nombre único utilizando UUID
    return os.path.join('media/', filename)  # Ruta de almacenamiento deseada


def ciclo_actual_genNombre():
    ahora = now()
    mes = ahora.month
    año = ahora.year
    # Determinar el ciclo actual
    if mes >= 8:
        ciclo = "Agosto - Diciembre"
    else:
        ciclo = "Enero - Junio"    
    return f"{ciclo} {año}"

def gen_fecha_nuevo_ciclo(ahora=None):
    if ahora is None:
        ahora = now()
    if ahora.month >= 8:
        # Si el mes actual es agosto o posterior, la nueva fecha será el 1 de agosto del próximo año
        nuevaFecha = date(ahora.year + 1, 8, 1)
    else:
        # Si el mes actual es anterior a agosto, la nueva fecha será el 1 de agosto del año actual
        nuevaFecha = date(ahora.year, 8, 1)
    return nuevaFecha

def ciclo_actual():
    # Obtener el último ciclo disponible               
    ultimoCiclo = Ciclo.objects.order_by('-id').first()
    nombreUltimoCiclo = ciclo_actual_genNombre()

    #verificamos si el ciclo actual todavia esta bigente
    if ultimoCiclo and ultimoCiclo.nombre == nombreUltimoCiclo:
        return ultimoCiclo
    #si no se crea un nuevo ciclo y se actualiza la fecha del proximo en la config de la convocatoria
    else:
        print('Creando nuevo ciclo')        
        nuevo_ciclo = Ciclo.objects.create(nombre=nombreUltimoCiclo)                
        return nuevo_ciclo     

def getCiclo(index=0):
    if index == 0:
        return ciclo_actual()
    else:
        ciclos = Ciclo.objects.order_by('-id').all()
        if len(ciclos) >= index:
            return ciclos[index]
        else:
            return None        

def ciclo_actual_pk():
    return ciclo_actual().pk   

class Ciclo(models.Model):                
    nombre = models.CharField(max_length=100, unique=True, default=ciclo_actual_genNombre)
    presupuesto = models.DecimalField(max_digits=11, decimal_places=2, blank=False, null=False, default=0.0)

    readonly_fields = ('nombre',)
    class Meta:
        ordering = ['-id']
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'        

    def __str__(self):
        return f'{self.nombre}'                      

#reciber para aztualizar otros modelos cuando inicia un nuevo ciclo
@receiver(post_save, sender=Ciclo)
def nuevo_ciclo(sender, instance, created, **kwargs):
    if created:
        print('Ciclo creado, actualizando configuraciones')
        modalidadesActivas = Modalidad.objects.filter(archivado=False)
        for modalidad in modalidadesActivas:
            ultimoMonto = MontoModalidad.objects.filter(modalidad=modalidad).order_by('-id').first()
            ultimoMontoval = None
            if ultimoMonto:
                ultimoMontoval = ultimoMonto.monto
            MontoModalidad.objects.create(modalidad=modalidad, ciclo=instance, monto=ultimoMontoval)

        


class SingletonModel(models.Model):
    """Singleton Django Model"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def get_object(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()

#clase de configuracion de convocatorias
class Convocatoria(SingletonModel):
    fecha_inicio = models.DateField(null=False, blank=False)
    fecha_cierre = models.DateField(null=False, blank=False)    
    archivo_convocatoria = models.FileField(upload_to=modalidadMediaPath, validators=[validador_pdf], verbose_name="Convocatoria", null=True)    
    ultimo_ciclo_publicado = models.ForeignKey(Ciclo, on_delete=models.SET_NULL, verbose_name=_("Ultimo ciclo publicado"), null=True, blank=True)

    def __str__(self):
        return f'Convocatoria {self.fecha_inicio} // {self.fecha_cierre}' #now().date()

    @property
    def mostrar_precio(self):
        return "%s" % self.presupuesto        
    
    @property
    def fecha_convocatoria(self):
        if self.fecha_inicio != None and ((now().date() >= self.fecha_inicio) and (now().date() <= self.fecha_cierre)):
            return True
        else:
            return False
        
    @property
    def mensaje_estado_convocatoria(self):        
        if self.fecha_inicio != None:
            if now().date() == self.fecha_cierre:
                return f'Último día de convocatoria.'
            elif now().date() < self.fecha_inicio:
                dias_restantes = (self.fecha_inicio - now().date()).days
                if dias_restantes < 2:
                    return f'Falta {dias_restantes} día para que inicie la convocatoria.'
                else:
                    return f'Faltan {dias_restantes} días para que inicie la convocatoria.'
            elif now().date() <= self.fecha_cierre:
                dias_restantes = (self.fecha_cierre - now().date()).days+1
                if dias_restantes < 2:
                    return f'Queda {dias_restantes} día para que la convocatoria termine.'
                else:
                    return f'Quedan {dias_restantes} días para que la convocatoria termine.'
            else:
                return 'La convocatoria ha terminado.'
        else:
            return 'Las fechas de la convocatoria no han sido definidas.'


class Modalidad(models.Model):
    TIPO_CHOICES = [
        ('Renovacion', 'Renovación'),
        ('Ingreso', 'Nuevo Ingreso')
    ]
    nombre = models.CharField(max_length=255, verbose_name="Nombre", null=False)
    imagen = models.ImageField(upload_to=modalidadMediaPath, verbose_name="Imagen", null=False)
    descripcion = models.TextField(verbose_name="Descripción", null=False)    
    mostrar = models.BooleanField(default=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_CHOICES[1][0])
    archivado = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nombre} ({self.tipo})'
    
    def get_documentos_children(self):
        return self.documento_set.all()
    
    class Meta:        
        ordering = ['nombre','tipo']

class MontoModalidad(models.Model):
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, verbose_name=_("Modalidad"), null=False, blank=False)
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, verbose_name=_("Ciclo"), null=False, blank=False)
    monto = models.DecimalField(max_digits=7, decimal_places=2,verbose_name=_("Monto"), null=False, blank=False, default=0.0)
    
    class Meta:        
        ordering = ['modalidad','-id']
        unique_together = ('modalidad', 'ciclo')

    def __str__(self):
        return f"monto '{self.modalidad}' - {self.ciclo}"

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
    
