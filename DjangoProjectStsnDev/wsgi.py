import os
import sys

# Укажите путь к вашему проекту
sys.path.insert(0, '/var/www/DjangoProjectStsnDev')

# Укажите путь к виртуальному окружению
sys.path.insert(0, '/var/www/DjangoProjectStsnDev/venv/lib/python3.13/site-packages')

# Установите переменную окружения для Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'DjangoProjectStsnDev.settings'

# Импортируйте и создайте WSGI приложение
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
