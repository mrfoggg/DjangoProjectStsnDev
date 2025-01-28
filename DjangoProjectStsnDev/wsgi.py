import os
import sys

# Укажите путь к виртуальному окружению
activate_this = '/var/www/DjangoProjectStsnDev/venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

sys.path.append('/var/www/DjangoProjectStsnDev')

os.environ['DJANGO_SETTINGS_MODULE'] = 'DjangoProjectStsnDev.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
