from __future__ import absolute_import, unicode_literals
import os
import sqlite3
from celery import Celery

# Установите режим WAL для SQLite
con = sqlite3.connect('celerydb.sqlite')
con.execute('PRAGMA journal_mode=WAL;')
con.close()

# Установите настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProjectStsnDev.settings')

app = Celery('DjangoProjectStsnDev')

# Используйте настройки Django для конфигурации Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находите задачи в приложениях
app.autodiscover_tasks()
