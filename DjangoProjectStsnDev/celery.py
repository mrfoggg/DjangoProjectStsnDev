from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите переменную окружения DJANGO_SETTINGS_MODULE, чтобы Celery мог найти настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProjectStsnDev.settings')

app = Celery('DjangoProjectStsnDev')

# Используйте Django для всех настроек Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически загружайте задачи из всех приложений Django
app.autodiscover_tasks()
