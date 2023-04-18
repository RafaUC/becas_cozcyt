from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator

""""
class EetudioSE(models.Model):
    VIVES_CHOICES = (
        ('1', 'Padres'),
        ('2', 'Familiares (tios, abuelos, etc.)'),
        ('3', 'Amigos'),
        ('4', 'Esposo(a)'),
    )

    ESTADO_CASA_CHOICES = (
        ('1', 'Propia'),
        ('2', 'Rentado'),
        ('3', 'Casa de huéspedes'),
        ('4', 'otro:'),
    )

    MATERIAL_PISO_CHOICES = (
        ('1','Tierra'),
        ('2','Madera'),
        ('3','Cemento'),
        ('4','Mosaico'),
        ('5','Alfombra'),
        ('6','Duela'),
        ('7','otro: '),
    )

    ocupacion = models.CharField(verbose_name="Ocupacion", max_length=191, blank=False, null=False)
    trabajas = models.BooleanField(verbose_name="Trabajas", blank=False, null=False)
    telefono_trabajo= models.IntegerField(verbose_name="Telefono del Trabajo", null=True, blank=False, validators=[MinLengthValidator(10), MaxLengthValidator(10)])
    Horario_trabajo_inicio = models.TimeField(verbose_name="Inicio Horario de Trabajo", null=True, blank=False)
    Horario_trabajo_final = models.TimeField(verbose_name="Final Horario de Trabajo", null=True, blank=False)
    sueldo_mensual = models.FloatField(verbose_name="Sueldo Mensual", blank=False, null=True)
    vives_con = models.CharField(verbose_name="Vives Con", max_length=191, blank=False, null=False, choices=VIVES_CHOICES)
    tiempo_viviendo = models.FloatField(verbose_name="Tiempo Viviendo Ahí", blank=False, null=False)
    personas_viviendo = models.PositiveIntegerField(verbose_name="Numero de personas vivendo ahí", blank=False, null=False)
    estatus_casa = models.CharField(verbose_name="Estatus del Domicilio", max_length=255, blank=False, null=False, choices=ESTADO_CASA_CHOICES)
    estatus_casa_otro = models.CharField(verbose_name="Otro Estado del domicilio", max_length=255, blank=True, null=False)
    material_piso = models.CharField(verbose_name="Material del Piso", max_length=255, blank=False, null=False, choices=MATERIAL_PISO_CHOICES)
    material_piso_otro = models.CharField(verbose_name="Otro Estado del domicilio", max_length=255, blank=True, null=False)
    cantidad_recamaras = models.PositiveIntegerField(verbose_name="cantidad de recamaras", blank=False, null=False)
    Cantidad_banos = models.PositiveIntegerField(verbose_name="Cantidad de Baños", blank=False, null=False)
    tiene_sala = models.BooleanField(verbose_name="Tiene Sala", blank=False, null=False)
    tiene_concina_independiente = models.BooleanField(
        verbose_name="Tiene concina Independiente", blank=False, null=False)
    servicios

    """
