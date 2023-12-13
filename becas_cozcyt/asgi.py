"""
ASGI config for becas_cozcyt project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.layers import get_channel_layer
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from .consumers import NotificacionConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becas_cozcyt.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    re_path(r'ws/notificaciones/$', NotificacionConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
