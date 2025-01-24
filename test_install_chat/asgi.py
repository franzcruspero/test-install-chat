import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_install_chat.settings")

application = get_asgi_application()
