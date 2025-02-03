from django.contrib import admin
from .models import ExtensionProxy
from .forms import ExtensionProxyForm  # Используем форму, которую мы определили ранее

class ExtensionProxyAdmin(admin.ModelAdmin):
    form = ExtensionProxyForm  # Указываем форму с переведёнными полями

    # Поля, которые будут отображаться в админке
    fields = ['name', 'version', 'secret_key', 'trial_period_days', 'name_en', 'name_ru', 'description_en', 'description_ru']

admin.site.register(ExtensionProxy, ExtensionProxyAdmin)
