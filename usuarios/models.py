from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError


class Estado(models.Model):
    nombre = models.CharField(verbose_name="Nombre Estado", max_length=191, null=False)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    estado = models.ForeignKey(Estado, verbose_name="Estado", on_delete=models.CASCADE)
    cve_mun = models.PositiveIntegerField(verbose_name="Clave Municipio", null=False)
    nombre = models.CharField(verbose_name="Nombre Municipio", max_length=191, null=False)    
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)

    def save(self, *args, **kwargs):
        # Generar el ID combinando estado y cve_mun como una cadena
        self.id = f"{self.estado_id}{self.cve_mun}"
        super(Municipio, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ['estado', 'nombre']
        unique_together = ('estado', 'cve_mun')

class Institucion(models.Model):
    nombre = models.CharField(verbose_name="Nombre Institución", max_length=191, null=False)
    puntos = models.IntegerField(verbose_name="Puntos", default=0)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']
        verbose_name="Institución"

class Carrera(models.Model):
    nombre = models.CharField(verbose_name="Nombre Carrera", max_length=191, null=False)
    puntos = models.IntegerField(verbose_name="Puntos", default=0)
    institucion = models.ForeignKey(Institucion, 
        verbose_name="Institución", null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)
    deleted_at = models.DateTimeField(verbose_name="deleted_at", null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']
        verbose_name="Carrera"

class UsuarioManager(BaseUserManager):
    def create_user(self, email, curp, nombre,  password=None, is_admin=False, is_staff=False, is_active=True):        
        user = self.model(
            email=self.normalize_email(email)
        )
        user.curp = curp
        user.nombre = nombre
        user.set_password(password)  # change password to hash
        user.is_superuser = is_admin
        user.is_staff = is_staff
        user.is_active = is_active
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, curp, nombre, password=None, **extra_fields):        
        user = self.model(
            email=self.normalize_email(email)
        )
        user.curp = curp
        user.nombre = nombre
        user.set_password(password)        
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    CURP_REGEX = r'^[A-Z]{1}[AEIOU]{1}[A-Z]{2}[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|1[0-9]|2[0-9]|3[0-1])[HM]{1}(AS|BC|BS|CC|CS|CH|CL|CM|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[0-9A-Z]{1}[0-9]{1}$'    

    nombre = models.CharField(
        verbose_name="Nombre", max_length=191, blank=False, null=True)    
    curp = models.CharField(
        verbose_name="CURP", max_length=18, 
        validators=[RegexValidator(CURP_REGEX,'Debe ser un CURP valido.')],
        blank=False, null=False, unique=True)
    email = models.EmailField(verbose_name="E-mail", blank=False, null=False, unique=True)
    is_staff = models.BooleanField(default=False)    
    is_active = models.BooleanField(default=True)    
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'curp'    
    REQUIRED_FIELDS = ['nombre','email']
    objects = UsuarioManager()

    def __str__(self):
        str = ""
        if self.is_superuser:
            str = str + "SuperUser "
        if self.is_staff:
            str = str + "Staff "
        return str + self.curp
    
    class Meta:        
        ordering = ['-is_superuser', 'id' ]

def only_int(value): 
    if value.isdigit()==False:
        raise ValidationError('El campo no debe contener caracteres alfabeticos.')

class Solicitante(Usuario):
    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )
    GRADO_CHOICES = [(f"{i:02d}", f"{i:02d}") for i in range(1, 16)]
    
    RFC_REGEX = r'^([A-ZÑ&]{3,4}) ?(?:- ?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])) ?(?:- ?)?([A-Z\d]{2})([A\d])$'
    FOLIO_REGEX = r'^[a-zA-Z]{4}[0-9]{4}$'
    GRADO_REGEX = r'^\d{1,2}$'

    folio = models.CharField(
        verbose_name="Folio" ,max_length=8, null=True, blank=True,
        validators=[
            RegexValidator(FOLIO_REGEX,'El folio debe tener 4 letras seguidas de 4 números.')])
    rfc = models.CharField(
        verbose_name="RFC", max_length=13, 
        validators=[RegexValidator(RFC_REGEX,'Debe tener el formato de un RFC valido.')],
        blank=False, null=True, unique=True)
    ap_paterno = models.CharField(
        verbose_name="Apellido Paterno", max_length=45, blank=False, null=True)
    ap_materno = models.CharField(
        verbose_name="Apellido Materno", max_length=45, blank=True, null=True)
    fecha_nacimiento = models.DateField (
        verbose_name="Fecha de Nacimiento", blank=False, null=True)
    genero = models.CharField(verbose_name="Genero", max_length=255, choices=GENERO_CHOICES)    
    g_etnico = models.BooleanField(
        verbose_name="Origen Etnico", blank=False, null=True)    
    municipio = models.ForeignKey(Municipio, verbose_name="Delegación/Municipio", null=True, blank=False, on_delete=models.CASCADE)
    colonia = models.CharField(
        verbose_name="Colonia/Fraccionamiento", max_length=255,blank=False, null=True)
    calle = models.CharField(
        verbose_name="Calle", max_length=255, blank=False, null=True)
    numero = models.CharField(verbose_name="Numero", max_length=5, blank=False, null=True)
    codigo_postal = models.CharField(verbose_name="Codigo Postal", max_length=5, blank=False, null=True, validators=[MinLengthValidator(5), MaxLengthValidator(5)])
    tel_cel = models.CharField(verbose_name="Telefono Celular", max_length=10, null=True, blank=False, validators=[MinLengthValidator(10), MaxLengthValidator(10)])
    tel_fijo = models.CharField(verbose_name="Telefono Fijo", max_length=10, null=True, blank=False, validators=[MinLengthValidator(5), MaxLengthValidator(10)])    
    grado = models.CharField(verbose_name="Grado", max_length=2, null=True, blank=False, choices=GRADO_CHOICES)

    promedio = models.FloatField(verbose_name="Promedio", null=True, blank=False)    
    carrera = models.ForeignKey(Carrera, 
        verbose_name="Carrera",  null=True, blank=False, on_delete=models.CASCADE)
    email_verified_at = models.DateTimeField(verbose_name="email_verified_at", null=True)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)

    def __str__(self):
        return self.nombre + " " + self.ap_paterno
        

    class Meta:
        verbose_name = "Solicitante"
        permissions = [
            ('permisos_solicitante', 'Permisos para solicitantes'), ] 


class PuntajeGeneral(models.Model):
    SECCION_CHOICES = (
        ('1-Genero', 'Género'),
        ('2-Ingresos', 'Ingresos'),        
        ('3-Tipo de solicitud', 'Tipo de solicitud'),
        ('4-Periodo', 'Periodo'),
        ('5-Promedio', 'Promedio'),
    )

    tipo = models.CharField(max_length=50, choices=SECCION_CHOICES, verbose_name='Tipo de Puntaje')
    nombre = models.CharField(max_length=255, verbose_name='Nombre')
    puntos = models.IntegerField(verbose_name='Puntos', default=0)

    def __str__(self):
        return f'({self.tipo}) {self.nombre}'

    class Meta:
        verbose_name = 'Puntaje General'
        verbose_name_plural = 'Puntajes Generales'
        ordering = ['tipo', 'id']

class PuntajeMunicipio(models.Model):
    municipio = models.OneToOneField(Municipio, on_delete=models.CASCADE, primary_key=True)
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return f"PuntajeMun de {self.municipio} - {self.puntos} puntos"