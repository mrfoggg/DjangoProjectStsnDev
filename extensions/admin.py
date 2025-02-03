# admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin

from DjangoProjectStsnDev import settings
from .models import ExtensionProxy
from .forms import ExtensionProxyForm


@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ("Основная информация", {
                'fields': ['name', 'version', 'secret_key', 'trial_period_days', 'file']
            }),
        ]

        field_groups = [
            ('Название', 'name'),
            ('Заголовок', 'title'),
            ('Краткое описание', 'short_description'),
            ('Полное описание', 'description'),
            ('Мета описание', 'meta_description')
        ]

        for group_name, field in field_groups:
            lang_fields = [f"{field}_{lang_code}" for lang_code, _ in settings.LANGUAGES]
            fieldsets.append((
                group_name,
                {'fields': lang_fields, 'classes': ('collapse',)}
            ))

        return fieldsets