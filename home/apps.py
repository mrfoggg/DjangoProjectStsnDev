from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home' # указывает на путь к вашему приложению (путь к приложению в контексте Python-модулей).
