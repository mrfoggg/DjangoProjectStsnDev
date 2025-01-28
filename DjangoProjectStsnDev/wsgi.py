import sys
import os

# Укажите путь к проекту
sys.path.append('/var/www/DjangoProjectStsnDev')

# Укажите путь к виртуальной среде
sys.path.insert(0, '/var/www/DjangoProjectStsnDev/venv/lib/python3.13/site-packages')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
