from django.contrib import admin
from .models import Seccion, Opcion, Respuesta, RTextoCorto, RTextoParrafo, ROpcionMultiple, RCasillas, RDesplegable, Elemento
# Register your models here.

admin.site.register(Seccion)
admin.site.register(Opcion)
admin.site.register(Respuesta)
admin.site.register(RTextoCorto)
admin.site.register(RTextoParrafo)
admin.site.register(ROpcionMultiple)
admin.site.register(RCasillas)
admin.site.register(RDesplegable)
admin.site.register(Elemento)