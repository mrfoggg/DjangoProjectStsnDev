from django.contrib import admin
from unfold.admin import ModelAdmin

from DjangoProjectStsnDev import settings
from .models import ExtensionProxy, ExtensionTranslation
from .forms import ExtensionProxyForm
from rich import  print, inspect


@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'description_current_language')

    # inspect(form, methods=True)


    def get_form(self, request, obj=None, change=False, **kwargs):
        print('LOCALS get_form - ', locals())
        # kwargs['fields'].extend(['title_en', 'title_uk'])
        return super(ExtensionProxyAdmin, self).get_form(request, obj, **kwargs)


    def get_fieldsets(self, request, obj=None):
        print('LOCALS get_fieldsets - ', locals())
        fieldsets = [
            ("Основная информация", {
                'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
            }),
        ]

        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in settings.LANGUAGES]

        # Простой способ динамически добавить поля для переводов
        for field in translatable_fields:
            field_fields = [f"{field.name}_{lang_code}" for lang_code in language_codes]
            fieldsets.append((field.name.capitalize(), {'fields': tuple(field_fields)}))

        return fieldsets
