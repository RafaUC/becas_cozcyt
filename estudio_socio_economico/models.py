from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from model_utils.managers import InheritanceManager
from usuarios.models import Solicitante
import uuid
from django.core.exceptions import ValidationError

class Seccion(models.Model):
    TIPOS_CHOICES = (
        ('único', 'Único'),
        ('agregación', 'Agregación'),
    )

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPOS_CHOICES)
    orden = models.IntegerField(verbose_name='orden', default=100_000)

    def __str__(self):
        return self.nombre
    
    class Meta:        
        ordering = ['orden' ]


class Opcion(models.Model):    
    elemento = models.ForeignKey('Elemento', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, verbose_name='Nombre Opción')
    orden = models.IntegerField(verbose_name='orden', default=100_000)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Opción'
        verbose_name_plural = 'Opciones'
        ordering = ['elemento','orden' ]


#----------Respuestas-------------

class CustomIntegerField(models.IntegerField):
    def __init__(self, *args, min_digits=None, max_digits=None, **kwargs):
        self.min_digits = min_digits
        self.max_digits = max_digits
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if self.min_digits is not None and len(str(value)) < self.min_digits:
            raise ValidationError(f"El valor debe tener almenos {self.min_digits} digitos.")
        if self.max_digits is not None and len(str(value)) > self.max_digits:
            raise ValidationError(f"El valor debe tener a lo mucho {self.max_digits} digitos.")

class Respuesta(models.Model):
    elemento = models.ForeignKey('Elemento', on_delete=models.CASCADE)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE)
    otro = None    

    objects = InheritanceManager()

    def __str__(self):
        return f"Respuesta - Elemento: {self.elemento} - Solicitante: {self.solicitante}"

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        unique_together = ['elemento', 'solicitante']

    def clean(self):
        if self.elemento.obligatorio and self.is_blank():
            raise ValidationError(f"La respuesta para '{self.elemento}' es obligatoria.")
        super().clean()

    def is_blank(self):
        raise NotImplementedError("Subclases de Respuesta deben implementar este método.")


class RNumerico(Respuesta):
    texto = models.CharField(max_length=255)
    
    def is_blank(self):
        return not self.texto.strip()

class RTextoCorto(Respuesta):
    texto = models.CharField(max_length=255)

    def is_blank(self):
        return not self.texto.strip()

class RTextoParrafo(Respuesta):
    texto = models.TextField()

    def is_blank(self):
        return not self.texto.strip()

class RHora(Respuesta):
    hora = models.TimeField()

    def is_blank(self):
        return self.hora is None

class RFecha(Respuesta):
    fecha = models.DateField()

    def is_blank(self):
        return self.fecha is None

class ROpcionMultiple(Respuesta):
    respuesta = models.ForeignKey(Opcion, on_delete=models.CASCADE, null=True, blank=True)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=False)

    def is_blank(self):
        return self.respuesta is None and not ((self.elemento.opcionOtro and self.otro.strip()) or not self.elemento.opcionOtro )

class RCasillas(Respuesta):
    respuestas = models.ManyToManyField(Opcion)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=False)

    def is_blank(self):
        return self.respuesta is None and not ((self.elemento.opcionOtro and self.otro.strip()) or not self.elemento.opcionOtro )

class RDesplegable(Respuesta):
    respuesta = models.ForeignKey(Opcion, on_delete=models.CASCADE)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=False)

    def is_blank(self):
        return self.respuesta is None and not ((self.elemento.opcionOtro and self.otro.strip()) or not self.elemento.opcionOtro )

#---------Elementos-----------

class Elemento(models.Model):
    TIPO_CHOICES = (
        ('separador', 'Separador'),
        ('numerico', 'Numérico'),                
        ('texto_corto', 'Texto Corto'),
        ('texto_parrafo', 'Texto Párrafo'),
        ('hora', 'Hora'),
        ('fecha', 'Fecha'),
        ('opcion_multiple', 'Opción Múltiple'),
        ('casillas', 'Casillas'),
        ('desplegable', 'Desplegable'),
    )

    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')    
    opcionOtro = models.BooleanField(default=True, verbose_name='Opcion Otro')    
    numMin = models.PositiveIntegerField(verbose_name='numMin', default=0)
    numMax = models.PositiveIntegerField(verbose_name='numMax', default=10)
    row = models.IntegerField(verbose_name='row', default=100_000)
    col = models.IntegerField(verbose_name='col', default=100_000)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')    

    def __str__(self):
        return self.nombre
    
    def getRespuestaModel(self):
        if self.tipo == 'texto_corto':
            return RTextoCorto
        elif self.tipo == 'texto_parrafo':
            return RTextoParrafo
        elif self.tipo == 'opcion_multiple':
            return ROpcionMultiple
        elif self.tipo == 'casillas':
            return RCasillas
        elif self.tipo == 'desplegable':
            return RDesplegable
        elif self.tipo == 'numerico':
            return RNumerico
        elif self.tipo == 'hora':
            return RHora
        elif self.tipo == 'fecha':
            return RFecha
        else:
            return None

    def crearRespuesta(self, solicitante):
        respuesta_model = self.getRespuestaModel()
        if respuesta_model:
            return respuesta_model.objects.create(elemento=self, solicitante=solicitante)
        else : 
            return None
    
    class Meta:
        verbose_name = 'Elemento'
        verbose_name_plural = 'Elementos'        
        ordering = ['seccion','row', 'col', ]
