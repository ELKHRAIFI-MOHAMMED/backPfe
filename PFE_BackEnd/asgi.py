import os
import django
from django.core.asgi import get_asgi_application

# Configuration initiale CRUCIALE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PFE_BackEnd.settings')
django.setup()  # Initialise explicitement Django

# Maintenant vous pouvez importer les autres composants
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from login_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})