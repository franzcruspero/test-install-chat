from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from django.conf import settings

# Set the default Django settings module for the "celery" program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_install_chat.settings")

app = Celery("test_install_chat")

# - namespace="CELERY" means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
