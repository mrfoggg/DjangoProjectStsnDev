from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ExtensionProxy, ExtensionTranslation
from .forms import ExtensionProxyForm

@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'description_current_language')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ("Основная информация", {
                'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
            }),
        ]
        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

        for field in translatable_fields:
            field_fields = []
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                field_fields.append(field_name)
            fieldsets.append((field.capitalize(), {'fields': tuple(field_fields)}))

        return fieldsets
