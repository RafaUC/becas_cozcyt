from .models import Notificacion


def nueva(solicitante, titulo, mensaje, redirect, plantilla='notificacion.html'):
    Notificacion.objects.create(solicitante=solicitante, titulo=titulo, mensaje=mensaje, redirect=redirect, plantilla=plantilla)

