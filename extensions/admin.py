from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ExtensionProxy
from .forms import ExtensionProxyForm

@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'description_current_language')
    fieldsets = (
        ("Основная информация", {
            'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
        }),
        ("Название", {
            'fields': ('name_en', 'name_ru', 'name_ua'),
        }),
        ("Описание", {
            'fields': ('description_en', 'description_ru', 'description_ua'),
        }),
        ("Title", {
            'fields': ('title_en', 'title_ru', 'title_ua'),
        }),
    )