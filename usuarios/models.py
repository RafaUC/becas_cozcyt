from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator


class Estado(models.Model):
    nombre = models.CharField(verbose_name="Nombre Estado", max_length=191, null=False)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=False)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)

    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    nombre = models.CharField(verbose_name="Nombre Municipio", max_length=191, null=False)
    estado = models.ForeignKey(Estado, verbose_name="Estado", on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=False)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)

    def __str__(self):
        return self.nombre

class Institucion(models.Model):
    nombre = models.CharField(verbose_name="Nombre Institucion", max_length=191, null=False)
    puntos = models.IntegerField(verbose_name="Puntos", null=True)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)


    def __str__(self):
        return self.nombre

class Carrera(models.Model):
    nombre = models.CharField(verbose_name="Nombre Carrera", max_length=191, null=False)
    puntos = models.IntegerField(verbose_name="Puntos")
    institucion = models.ForeignKey(Institucion, 
        verbose_name="Instituciones", null=False, blank=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True, null=False)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True, null=True)
    deleted_at = models.DateTimeField(verbose_name="deleted_at", null=True)

    def __str__(self):
        return self.nombre

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
        user.active = is_active
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
        user.active = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(
        verbose_name="Nombre", max_length=191, blank=False, null=True)    
    curp = models.CharField(
        verbose_name="CURP", max_length=18, 
        validators=[RegexValidator(r'^[a-zA-Z0-9]{18}$', 'Debe tener exactamente 18 caracteres alfanuméricos.')],
        blank=False, null=False, unique=True)
    email = models.EmailField(verbose_name="E-mail", blank=False, null=False, unique=True)
    is_staff = models.BooleanField(default=False)    
    
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


class Solicitante(Usuario):
    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )

    rfc = models.CharField(
        verbose_name="RFC", max_length=13, 
        validators=[RegexValidator(r'^[A-Za-zñÑ&]{3,4}\d{6}\w{3}$', 'Debe tener el formato de un RFC.')],
        blank=False, null=True, unique=True)
    ap_paterno = models.CharField(
        verbose_name="Apellido Paterno", max_length=45, blank=False, null=True)
    ap_materno = models.CharField(
        verbose_name="Apellido Materno", max_length=45, blank=True, null=True)
    fecha_nacimiento = models.DateField (
        verbose_name="Fecha de Nacimiento", blank=False, null=True)
    genero = models.CharField(verbose_name="Genero", max_length=255, choices=GENERO_CHOICES)
    edad = models.IntegerField(verbose_name="Edad", blank=False, null=True)
    g_etnico = models.BooleanField(
        verbose_name="Origen Etnico", blank=False, null=True)    
    municipio = models.ForeignKey(Municipio, verbose_name="Municipio", null=True, blank=False, on_delete=models.CASCADE)
    colonia = models.CharField(
        verbose_name="Colonia", max_length=255,blank=False, null=True)
    calle = models.CharField(
        verbose_name="Calle", max_length=255, blank=False, null=True)
    numero = models.CharField(verbose_name="Numero", max_length=5, blank=False, null=True)
    codigo_postal = models.IntegerField(verbose_name="Codigo Postal", blank=False, null=True, validators=[MinLengthValidator(5), MaxLengthValidator(5)])
    tel_cel = models.IntegerField(verbose_name="Telefono Celular", null=True, blank=False, validators=[MinLengthValidator(10), MaxLengthValidator(10)])
    tel_fijo = models.IntegerField(verbose_name="Telefono Fijo", null=True, blank=False, validators=[MinLengthValidator(5), MaxLengthValidator(10)])
    Grado = models.IntegerField(verbose_name="Grado", null=True, blank=False, validators=[MinLengthValidator(1),MaxLengthValidator(2)])
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


