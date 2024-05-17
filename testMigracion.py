import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
django.setup()
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Solicitante, Usuario, SiteColor
from django.conf import settings
from django.contrib.auth.models import Permission, Group, User



load_colors_from_css()