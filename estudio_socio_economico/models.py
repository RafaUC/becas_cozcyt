from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from model_utils.managers import InheritanceManager
from usuarios.models import Solicitante

class Seccion(models.Model):
    TIPOS_CHOICES = (
        ('único', 'Único'),
        ('agregación', 'Agregación'),
    )

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPOS_CHOICES)

    def __str__(self):
        return self.nombre


class Opcion(models.Model):    
    nombre = models.CharField(max_length=255, verbose_name='Nombre Opción')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Opción'
        verbose_name_plural = 'Opciones'


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

    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    obligatorio = models.BooleanField(default=True, verbose_name='Obligatorio')
    lookup_id = models.UUIDField(verbose_name='Lookup ID')
    order = models.IntegerField(verbose_name='Orden')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name='Tipo')
    opciones = None

    respuestaModel = None
    objects = InheritanceManager()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Elemento'
        verbose_name_plural = 'Elementos'


class ElementoSeparador(Elemento):
    respuestaModel = None    

    class Meta:
        verbose_name = 'Elemento Separador'


class ElementoTextoCorto(Elemento):
    respuestaModel = RTextoCorto
    

    class Meta:
        verbose_name = 'Elemento Texto Corto'


class ElementoTextoParrafo(Elemento):
    respuestaModel = RTextoParrafo    

    class Meta:
        verbose_name = 'Elemento Texto Párrafo'
        


class ElementoOpcionMultiple(Elemento):
    respuestaModel = ROpcionMultiple
    opciones = models.ManyToManyField(Opcion)

    class Meta:
        verbose_name = 'Elemento Opción Múltiple'


class ElementoCasillas(Elemento):
    respuestaModel = RCasillas
    opciones = models.ManyToManyField(Opcion)

    class Meta:
        verbose_name = 'Elemento Casillas'


class ElementoDesplegable(Elemento):
    respuestaModel = RDesplegable
    opciones = models.ManyToManyField(Opcion)

    class Meta:
        verbose_name = 'Elemento Desplegable'


