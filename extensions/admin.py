from django.contrib import admin
from django import forms
from unfold.admin import ModelAdmin
from .models import ExtensionProxy, ExtensionTranslation
from .forms import ExtensionProxyForm

@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'description_current_language')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

        for field in translatable_fields:
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                if field_name not in form.base_fields:
                    form.base_fields[field_name] = forms.CharField(required=False)

        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

        for field in translatable_fields:
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                if field == 'name':
                    fieldsets[1][1]['fields'] += (field_name,)
                elif field == 'title':
                    fieldsets[2][1]['fields'] += (field_name,)
                elif field == 'short_description':
                    fieldsets[3][1]['fields'] += (field_name,)
                elif field == 'description':
                    fieldsets[4][1]['fields'] += (field_name,)
                elif field == 'meta_description':
                    fieldsets[5][1]['fields'] += (field_name,)

        return fieldsets

    fieldsets = (
        ("Основная информация", {
            'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
        }),
        ("Название", {
            'fields': tuple(),
        }),
        ("Заголовок", {
            'fields': tuple(),
        }),
        ("Краткое описание", {
            'fields': tuple(),
        }),
        ("Полное описание", {
            'fields': tuple(),
        }),
        ("Поисковое описание", {
            'fields': tuple(),
        }),
    )
