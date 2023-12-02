from django.db.models import Max
from .models import Documento


def get_max_order(modalidad) -> int:
    existing_docs = Documento.objects.filter(modalidad=modalidad)
    if not existing_docs.exists():
        return 1
    else:
        current_max = existing_docs.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1