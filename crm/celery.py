from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('crm')

# Load settings from Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks automatically from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
