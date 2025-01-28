import os
import sys

# Укажите путь к вашему проекту
sys.path.insert(0, '/var/www/DjangoProjectStsnDev')

# Укажите путь к виртуальному окружению
activate_this = '/var/www/DjangoProjectStsnDev/venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

os.environ['DJANGO_SETTINGS_MODULE'] = 'DjangoProjectStsnDev.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
