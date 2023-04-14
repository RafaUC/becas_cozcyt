import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Solicitante
from django.contrib.auth.models import Permission, Group, User

administradores = Group.objects.get_or_create(name='administradores')
solicitantes = Group.objects.get_or_create(name='solicitantes')

content_type_administrador = ContentType.objects.get_for_model(User)
content_type_solicitante = ContentType.objects.get_for_model(Solicitante)

permisos_administrador = Permission.objects.get_or_create(
    codename='permiso_administrador',
    name="Permiso para el grupo administradores",
    content_type=content_type_administrador
)
permisos_solicitante = Permission.objects.get_or_create(
    codename='permiso_solicitante',
    name="Permiso para el grupo solicitantes",
    content_type=content_type_solicitante
)