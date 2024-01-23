from django.db import models
from usuarios.models import Solicitante
from modalidades.models import Modalidad, Documento, ciclo_actual
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from uuid import uuid4
import os
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from usuarios.models import PuntajeGeneral, PuntajeMunicipio
from estudio_socio_economico.models import Elemento, RNumerico

from mensajes import notificaciones as notif
# Create your models here.


class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('docRevicion', 'Documentación en revisión'),
        ('docError', 'Documentación erronea'),
        ('docAprobada', 'Documentación aprobada'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]
    TIPO_CHOICES = [
        ('renovacion', 'Renovación'),
        ('ingreso', 'Nuevo Ingreso')
    ]

    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, null=False)
    solicitante = models.ForeignKey(Solicitante, on_delete=models.CASCADE, null=False)
    ciclo = models.CharField(max_length=50, default=ciclo_actual(), editable=False, null=False)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_CHOICES[0][0])
    puntaje = models.IntegerField(default=0) 
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_CHOICES[1][0])

    readonly_fields = ('ciclo',)
    class Meta:
        ordering = ['-puntaje','-id']
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        unique_together = ('modalidad', 'ciclo','solicitante')
    
    # def __str__(self):
    #     return f'Solicitud object ({self.id}) p:{self.puntaje}'

    def __str__(self):
        return f'{self.modalidad}/  {self.solicitante}/  {self.ciclo} / p:{self.puntaje}'


#Señal para calcular y actualizar el puntaje de una solicitud y su tipo
@receiver(pre_save, sender=Solicitud)
def calcular_puntaje(sender, instance, **kwargs):    
    nuevoPuntaje = 0
    solicitante = instance.solicitante
    seccionChoices = PuntajeGeneral.SECCION_CHOICES    

    #Procesando puntajes generales
    #Genero
    try:
        puntajes = PuntajeGeneral.objects.filter(tipo = seccionChoices[0][0])    
        for puntaje in puntajes:
            if solicitante.genero == puntaje.nombre:
                nuevoPuntaje += puntaje.puntos
                break
    except Exception as e:        
        print(f"No se pudo calcular el puntaje de generos: {e}")
    #Ingresos
    try:
        puntajes = PuntajeGeneral.objects.filter(tipo = seccionChoices[1][0])
        ingresos = [] #lista de querysets relacionados con ingresos    
        q = Q(**{'nombre__icontains': 'Sueldo mensual familiar'}) #| Q(**{'nombre__icontains': 'ingreso'})
        ingresoPreguntas = Elemento.objects.filter(tipo=Elemento.TIPO_CHOICES[1][0]).filter(q)    
        ids_preguntas = ingresoPreguntas.values_list('id', flat=True)
        # Obtener todas las respuestas que pertenecen a las preguntas
        respuestas = RNumerico.objects.filter(elemento__id__in=ids_preguntas, solicitante=solicitante)    
        ingresos = respuestas.values_list('valor', flat=True)
        ingresos = list(map(int, ingresos))        
        ingresoTotal = sum(ingresos)        
        for puntaje in puntajes:
            limite_inferior, limite_superior = map(int, puntaje.nombre.replace('$', '').split('-'))
            if limite_inferior <= ingresoTotal <= limite_superior:
                nuevoPuntaje += puntaje.puntos
                break
    except Exception as e:        
        print(f"No se pudo calcular el puntaje de Ingresos : {e}")
    #tipo de solicitud
    try:                
        if solicitante.es_renovacion:
            puntaje = PuntajeGeneral.objects.get(tipo = seccionChoices[2][0], nombre='Renovación')
            instance.tipo = Solicitud.TIPO_CHOICES[0][0]
            nuevoPuntaje += puntaje.puntos
        else:
            puntaje = PuntajeGeneral.objects.get(tipo = seccionChoices[2][0], nombre='Nuevo ingreso')
            instance.tipo = Solicitud.TIPO_CHOICES[1][0]
            nuevoPuntaje += puntaje.puntos
    except Exception as e:        
        print(f"No se pudo calcular el puntaje y tipo de Tipo Solicitud: {e}")
    #periodo
    try:
        puntajes = PuntajeGeneral.objects.filter(tipo = seccionChoices[3][0])
        for puntaje in puntajes:
            limite_inferior, limite_superior = map(int, puntaje.nombre.split('-'))
            if limite_inferior <= int(solicitante.grado) <= limite_superior:
                nuevoPuntaje += puntaje.puntos
                break
    except Exception as e:        
        print(f"No se pudo calcular el puntaje de periodo: {e}")
    #promedio
    try:
        puntajes = PuntajeGeneral.objects.filter(tipo = seccionChoices[4][0])        
        for puntaje in puntajes:
            limite_inferior, limite_superior = map(float, puntaje.nombre.split('-'))            
            if limite_inferior <= solicitante.promedio <= limite_superior:
                nuevoPuntaje += puntaje.puntos
                break
    except Exception as e:        
        print(f"No se pudo calcular el puntaje de promedio: {e}")
    #municipio
    try:
        puntajeMun = PuntajeMunicipio.objects.get(municipio=solicitante.municipio_id)
        nuevoPuntaje += puntajeMun.puntos
    except PuntajeMunicipio.DoesNotExist:
        print(f"puntaje municipio 0:")
    except Exception as e:        
        print(f"No se pudo calcular el puntaje de municipio: {e}")
    #Institucion y carrera
    try:
        carrera = solicitante.carrera
        nuevoPuntaje += carrera.puntos
        nuevoPuntaje += carrera.institucion.puntos
    except Exception as e:        
        print(f"No se pudo calcular el puntaje de Institución y carrera: {e}")
    
    instance.puntaje = nuevoPuntaje



def validador_pdf(value):
    ext = os.path.splitext(value.name)[1]  # Obtener la extensión del archivo
    valid_extensions = ['.pdf']  # Lista de extensiones permitidas
    if ext.lower() not in valid_extensions:
        raise ValidationError(_('Sólo se permiten archivos en formato PDF.'))

def validate_file_size(value):
   filesize = value.size
   if filesize > 1048576: # 1MB
       raise ValidationError("El archivo es demasiado grande. El tamaño máximo permitido es 1MB.")

def documentoMediaPath(instance, filename):
    ext = filename.split('.')[-1]  # Obtiene la extensión del archivo
    filename = f"{uuid4().hex}.{ext}"  # Genera un nombre único utilizando UUID
    return os.path.join("protected_uploads/", filename)  #Obtener la ruta de la carpeta que se va a crear por solicitud


class RespuestaDocumento(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Revisión pendiente'),
        ('aprobado', 'Aprobado'),
        ('denegado', 'Denegado'),
    ]
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    file = models.FileField(upload_to=documentoMediaPath, validators=[validador_pdf, validate_file_size])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_CHOICES[0][0])

    
    def __str__(self):
        return f'{self.solicitud}/ {self.documento}'
    
    @property
    def filename(self) -> str:
        return os.path.basename(self.file.name)

    class Meta:
        verbose_name = 'Documento de Respuesta'
        verbose_name_plural = 'Documentos de Respuesta'
        unique_together = ('solicitud', 'documento')

#Signal que despues guardar algun RespuestaDocumento verifica que la solicitud a la que pertenece
#cumple con las condiciones para pasar a estado docAprobada o no
@receiver(post_save, sender=RespuestaDocumento)
def actualizar_estado_solicitud(sender, instance, **kwargs):    
    # Verificar condiciones y actualizar estado de la solicitud       
    opc = -1    
    solicitud = instance.solicitud    
          
    # Verificar que existan todas las instancias necesarias de RespuestaDocumento
    documentos_modalidad = solicitud.modalidad.documento_set.all()
    respuestas_documentos_solicitud = RespuestaDocumento.objects.filter(solicitud=solicitud)                
    # si Todas las instancias necesarias de RespuestaDocumento existen
    if set(documentos_modalidad) == set({resp.documento for resp in respuestas_documentos_solicitud}):        

        # Verificar que todas las instancias de RespuestaDocumento de la solicitud estén aprobadas            
        if respuestas_documentos_solicitud.filter(estado=RespuestaDocumento.ESTADO_CHOICES[1][0]).count() == respuestas_documentos_solicitud.count():
            # Todas las instancias de RespuestaDocumento de la solicitud están aprobadas
            opc = 0
        #si existe algun documento como denegado entonces es denegado
        elif respuestas_documentos_solicitud.filter(estado=RespuestaDocumento.ESTADO_CHOICES[2][0]).exists():
            opc = 1            
    else: #falta algun documento                
        opc = 1
      
    estadoActual = solicitud.estado
    if opc == 0:
        solicitud.estado = Solicitud.ESTADO_CHOICES[2][0] #'docAprobada'   
    elif opc == 1:
        solicitud.estado = Solicitud.ESTADO_CHOICES[1][0] #'docError'
    else:
        respuestas_documentos_solicitud = RespuestaDocumento.objects.filter(solicitud=solicitud)      
        #Si no hay ninguna respuestaDocumento denegada setear a docRevicion
        if respuestas_documentos_solicitud.filter(estado='denegado').count() <= 0:   
            if estadoActual != Solicitud.ESTADO_CHOICES[0][0]:
                notif.nueva(solicitud.solicitante,'Solicitud enviada con éxito y esperando por revisión. Favor de estar al tanto de actualizaciones.', 'solicitudes:historial')
            solicitud.estado = Solicitud.ESTADO_CHOICES[0][0] #'docRevicion'      
    
    if estadoActual != solicitud.estado:
        solicitud.save()
