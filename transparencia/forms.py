from django import forms
from modalidades.models import Modalidad, MontoModalidad, Ciclo, ciclo_actual

class ModalidadChoiceFieldNT(forms.ModelChoiceField):
   def label_from_instance(self, modalidad):
        return f"{modalidad.nombre}"


class ModalidadSelectForm(forms.Form):    
    def __init__(self, *args, **kwargs):
        ciclo = kwargs.pop('ciclo', None)
        if ciclo is None:
            raise ValueError("El argumento 'ciclo' es obligatorio")
        super().__init__(*args, **kwargs)
        cicloActual = ciclo_actual()
        modalidades_ids = MontoModalidad.objects.filter(ciclo=ciclo).values_list('modalidad_id', flat=True).distinct()
        if ciclo.id == cicloActual.id:            
            modalidades = Modalidad.objects.filter(id__in=modalidades_ids, mostrar=True, archivado=False)
        else:            
            modalidades = Modalidad.objects.filter(id__in=modalidades_ids)
        
        modalidadesAgregadas = set()
        
        for modalidad in modalidades.all():
            # Verificar si el nombre de la persona ya está en el conjunto de nombres agregados            
            if modalidad.nombre in modalidadesAgregadas:
                modalidades = modalidades.exclude(id=modalidad.id)
            modalidadesAgregadas.add(modalidad.nombre)                            
        
        self.fields['modalidad'] = ModalidadChoiceFieldNT(
            queryset=modalidades,
            label="Modalidad",
            widget=forms.Select(attrs={'class': 'form-control border-1 form-select', 'aria-label': "Modalidad"}),
        )


