from django.contrib import admin
from unfold.admin import ModelAdmin

from DjangoProjectStsnDev import settings
from .forms import ExtensionForm
from .models import ExtensionTranslation, Extension
from rich import  print, inspect


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionForm
    list_display = ('name', )

    def get_fieldsets(self, request, obj=None):
        print('LOCALS get_fieldsets - ', locals())
        fieldsets = [
            ("Основная информация", {
                'fields': (('name', 'version'), ('secret_key', 'trial_period_days')),
            }),
        ]

        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in settings.LANGUAGES]

        # Простой способ динамически добавить поля для переводов
        for field in translatable_fields:
            field_fields = [f"{field.name}_{lang_code}" for lang_code in language_codes]
            fieldsets.append((field.name.capitalize(), {'fields': tuple(field_fields)}))

        return fieldsets
