from django.db import models, IntegrityError
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
        ('unico', 'Único'),
        ('agregacion', 'Agregación'),
    )

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPOS_CHOICES)
    orden = models.IntegerField(verbose_name='orden', default=100_000)

    def __str__(self):
        return self.nombre
    
    class Meta:        
        ordering = ['orden' ]


class Opcion(models.Model):    
    elemento = models.ForeignKey('Elemento', on_delete=models.CASCADE, null=True, blank=True)
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

class RAgregacion(models.Model):
    # El modelo solo contiene el campo de identificación (ID) de forma predeterminada
    pass

class Respuesta(models.Model):
    rAgregacion = models.ForeignKey(RAgregacion, on_delete=models.CASCADE, null=True, blank=True)
    elemento = models.ForeignKey('Elemento', on_delete=models.CASCADE)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE)
    otro = None    

    objects = InheritanceManager()

    def __str__(self):
        return f"Respuesta {type(self)} - Elemento: {self.elemento} - Solicitante: {self.solicitante_id}"
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            # Solo realiza la verificación si estás creando una respuesta nueva
            if self.elemento.seccion.tipo == 'unico':
                # Verificar si ya existe una respuesta para esta combinación
                if Respuesta.objects.filter(elemento=self.elemento, solicitante=self.solicitante).exists():                    
                    raise IntegrityError('Ya existe una respuesta para este elemento y solicitante')
        super().save(*args, **kwargs)

    class Meta:        
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'   
    
    def getStringValue(self):
        return 'Respuesta no Implementado'


class RNumerico(Respuesta):
    valor = models.CharField(max_length=255, null=True,  blank=True)

    def getStringValue(self):
        if self.valor is None:
            return '-----'
        else :
            return str(self.valor)         
        

class RTextoCorto(Respuesta):
    texto = models.CharField(max_length=255, null=True,  blank=True)

    def getStringValue(self):
        if self.texto is None:
            return '-----'
        else :
            return str(self.texto) 


class RTextoParrafo(Respuesta):
    texto = models.TextField(null=True,  blank=True)

    def getStringValue(self):
        if self.texto is None:
            return '-----'
        else :
            return str(self.texto)        


class RHora(Respuesta):
    hora = models.TimeField(null=True,  blank=True)

    def getStringValue(self):
        if self.hora is None:
            return '-----'
        else :
            return str(self.hora)        


class RFecha(Respuesta):
    fecha = models.DateField(null=True,  blank=True)

    def getStringValue(self):
        if self.fecha is None:
            return '-----'
        else :
            return str(self.fecha)
    

class ROpcionMultiple(Respuesta):
    respuesta = models.ForeignKey(Opcion, on_delete=models.CASCADE, null=True, blank=True)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True,  blank=True)

    def getStringValue(self):
        if self.respuesta and self.respuesta.nombre == 'Otro':
            return str(self.respuesta)+': '+str(self.otro)
        else :
            if self.respuesta is None:
                return '-----'
            else :
                return str(self.respuesta)

class RCasillas(Respuesta):
    respuesta = models.ManyToManyField(Opcion,  blank=True)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True, blank=True)

    def getStringValue(self):
        string = ''
        objs = self.respuesta.all()
        for i, obj in enumerate(objs):
            string += str(obj)
            if obj.nombre == 'Otro':
                string += ': '+ str(self.otro)
            if i < len(objs) - 1:
                string += ', '
        if string == '':
            return '-----'
        else :           
            return string
    

class RDesplegable(Respuesta):
    respuesta = models.ForeignKey(Opcion, on_delete=models.CASCADE, null=True,  blank=True)
    otro = models.CharField(max_length=255, verbose_name="Otro", null=True,  blank=True)

    def getStringValue(self):
        if self.respuesta and self.respuesta.nombre == 'Otro':
            return str(self.respuesta)+': '+str(self.otro)
        else :
            if self.respuesta is None:
                return '-----'
            else :
                return str(self.respuesta)
    

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
