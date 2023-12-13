from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from mensajes.models import Notificacion

class Command(BaseCommand):
    help = 'Elimina registros más antiguos de 3 meses'

    def handle(self, *args, **options):
        delete_old_notif()
        self.stdout.write(self.style.SUCCESS('Registros eliminados con éxito'))

def delete_old_notif():
    print('Borrando notificaciones mas antiguas a 3 meses')
    three_months_ago = timezone.now() - timedelta(days=90)
    Notificacion.objects.filter(timestamp__lt=three_months_ago).delete()
