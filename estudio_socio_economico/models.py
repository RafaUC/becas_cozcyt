from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from model_utils.managers import InheritanceManager
from usuarios.models import Solicitante
import uuid

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
        

class RTextoCorto(Respuesta):
    texto = models.CharField(max_length=255)


class RTextoParrafo(Respuesta):
    texto = models.TextField()


class ROpcionMultiple(Respuesta):
    respuesta = models.ForeignKey(Opcion, on_delete=models.CASCADE)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=False)


class RCasillas(Respuesta):
    respuestas = models.ManyToManyField(Opcion)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=False)


class RDesplegable(Respuesta):
    respuesta = models.ForeignKey(Opcion, on_delete=models.CASCADE)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=False)




#---------Elementos-----------

class Elemento(models.Model):
    TIPO_CHOICES = (
        ('separador', 'Separador'),
        ('texto_corto', 'Texto Corto'),
        ('texto_parrafo', 'Texto Párrafo'),
        ('opcion_multiple', 'Opción Múltiple'),
        ('casillas', 'Casillas'),
        ('desplegable', 'Desplegable'),
    )

    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')    
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
        else:
            return None

    class Meta:
        verbose_name = 'Elemento'
        verbose_name_plural = 'Elementos'        
        ordering = ['seccion','row', 'col', ]
