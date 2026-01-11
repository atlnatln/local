"""
Celery configuration for Anka Backend.
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.dev')

app = Celery('anka_backend')

# Load configuration from Django settings, all configuration keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
