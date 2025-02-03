# admin.py
from django import forms
from django.contrib import admin
from django.utils.module_loading import import_string
from unfold.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from DjangoProjectStsnDev import settings
from extensions.models import ExtensionTranslation, Extension


class TranslationFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_translation_fields()

    def _add_translation_fields(self):
        for lang_code, lang_name in settings.LANGUAGES:
            for field in ExtensionTranslation.get_translatable_fields():
                field_key = f'{field}_{lang_code}'
                widget_class = import_string(self.Meta.widgets.get(field, 'django.forms.TextInput'))
                self.fields[field_key] = forms.CharField(
                    label=f"{field} ({lang_code.upper()})",
                    required=False,
                    widget=widget_class()
                )


class ExtensionAdminForm(TranslationFormMixin, forms.ModelForm):
    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'file']
        widgets = {
            'description': 'django.forms.Textarea',
            'meta_description': 'django.forms.Textarea',
            'short_description': 'django.forms.TextInput',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self._load_translations()

    def _load_translations(self):
        translations = {
            t.language_code: t for t in self.instance.translations.all()
        }
        for lang_code, _ in settings.LANGUAGES:
            translation = translations.get(lang_code)
            if translation:
                for field in ExtensionTranslation.get_translatable_fields():
                    field_key = f'{field}_{lang_code}'
                    self.fields[field_key].initial = getattr(translation, field, '')

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self._save_translations(instance)
        return instance

    def _save_translations(self, instance):
        for lang_code, _ in settings.LANGUAGES:
            translation_data = {
                field: self.cleaned_data.get(f'{field}_{lang_code}', '')
                for field in ExtensionTranslation.get_translatable_fields()
            }

            ExtensionTranslation.objects.update_or_create(
                extension=instance,
                language_code=lang_code,
                defaults=translation_data
            )


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_fieldsets(self, request, obj=None):
        # Основные поля
        fieldsets = [
            (None, {
                'fields': [
                    'name', 'version', 'secret_key',
                    'trial_period_days', 'file'
                ]
            }),
        ]

        # Группировка переводов по полям
        translation_fields = [
            ('Название', 'name'),
            ('Заголовок', 'title'),
            ('Краткое описание', 'short_description'),
            ('Описание', 'description'),
            ('Мета-описание', 'meta_description')
        ]

        # Создаем секцию для каждого поля с переводами
        for field_label, field_name in translation_fields:
            translated_fields = [
                f'{field_name}_{lang_code}'
                for lang_code, _ in settings.LANGUAGES
            ]

            fieldsets.append((
                field_label, {
                    'fields': translated_fields,
                    'classes': ('collapse',)
                }
            ))

        return fieldsets