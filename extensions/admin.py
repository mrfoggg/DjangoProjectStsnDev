from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ExtensionProxy
from .forms import ExtensionProxyForm

@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'name_en', 'name_ru', 'description_en', 'description_ru')
    fieldsets = (
        ("Основная информация", {
            'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
        }),
        ("Название", {
            'fields': ('name_en', 'name_ru'),
        }),
        ("Описание", {
            'fields': ('description_en', 'description_ru'),
        }),
    )
