from django.contrib import admin
from .models import Seccion, Opcion, Respuesta, RTextoCorto, RTextoParrafo, ROpcionMultiple, RCasillas, RDesplegable, RNumerico, RHora, RFecha , Elemento
# Register your models here.

class ElementoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'row', 'col')



admin.site.register(Seccion)
admin.site.register(Opcion)
admin.site.register(Respuesta)
admin.site.register(RTextoCorto)
admin.site.register(RTextoParrafo)
admin.site.register(ROpcionMultiple)
admin.site.register(RCasillas)
admin.site.register(RDesplegable)
admin.site.register(RNumerico)
admin.site.register(RHora)
admin.site.register(RFecha)
admin.site.register(Elemento, ElementoAdmin)