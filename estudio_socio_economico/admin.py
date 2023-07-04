from django.contrib import admin
from .models import Seccion, Opcion, Respuesta, RTextoCorto, RTextoParrafo, ROpcionMultiple, RCasillas, RDesplegable, Elemento, ElementoSeparador, ElementoTextoCorto, ElementoTextoParrafo, ElementoOpcionMultiple, ElementoCasillas, ElementoDesplegable
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
admin.site.register(ElementoSeparador)
admin.site.register(ElementoTextoCorto)
admin.site.register(ElementoTextoParrafo)
admin.site.register(ElementoOpcionMultiple)
admin.site.register(ElementoCasillas)
admin.site.register(ElementoDesplegable)