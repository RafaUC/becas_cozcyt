from django.contrib import admin
from .models import Modalidad, Documento, Convocatoria, Ciclo
# Register your models here.

admin.site.register(Modalidad)
admin.site.register(Documento)
admin.site.register(Convocatoria)
admin.site.register(Ciclo)