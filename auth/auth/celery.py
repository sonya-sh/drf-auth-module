
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth.settings')

app = Celery('auth')

# загружает настройки Celery из объекта django.conf.settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# автоматически обнаруживает и регистрирует задачи Celery из всех приложений в проекте Django. 
# Это позволяет Celery найти и запустить задачи, определенные в приложениях Django без явного указания.
app.autodiscover_tasks() 
