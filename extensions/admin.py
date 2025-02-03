from django import forms
from django.contrib import admin
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

    fieldsets = (
        ("Основная информация", {
            'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
        }),
        ("Название", {
            'fields': ('name_en', 'name_ru', 'name_uk'),
        }),
        ("Заголовок", {
            'fields': ('title_en', 'title_ru', 'title_uk'),
        }),
        ("Краткое описание", {
            'fields': ('short_description_en', 'short_description_ru', 'short_description_uk'),
        }),
        ("Полное описание", {
            'fields': ('description_en', 'description_ru', 'description_uk'),
        }),
        ("Поисковое описание", {
            'fields': ('meta_description_en', 'meta_description_ru', 'meta_description_uk'),
        }),
    )
