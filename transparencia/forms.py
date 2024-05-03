from django import forms
from modalidades.models import Modalidad

class ModalidadSelectForm(forms.Form):
    modalidad = forms.ModelChoiceField(
        queryset=Modalidad.objects.filter(mostrar=True),
        label="Modalidad",
        widget=forms.Select(attrs={'class': 'form-control border-1 form-select', 'aria-label': "Modalidad"}),
    )

    def __init__(self, *args, **kwargs):
        super(ModalidadSelectForm, self).__init__(*args, **kwargs)
        self.fields['modalidad'].initial = Modalidad.objects.filter(mostrar=True).first()