import sys
import os

# Путь к вашему виртуальному окружению
sys.path.insert(0, '/var/www/DjangoProjectStsnDev')

# Указываем путь к файлу settings.py
os.environ['DJANGO_SETTINGS_MODULE'] = 'DjangoProjectStsnDev.settings'

# Импортируем Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
