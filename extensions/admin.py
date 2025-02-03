# admin.py
from django import forms
from django.contrib import admin
from django.utils.module_loading import import_string
from unfold.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from DjangoProjectStsnDev import settings
from extensions.models import ExtensionTranslation, Extension


class ExtensionAdminForm(forms.ModelForm):
    # Явно объявляем поля перевода как атрибуты класса
    declared_fields = {}

    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'file']

    def __init__(self, *args, **kwargs):
        # Создаем поля перевода перед вызовом super()
        for lang_code, _ in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_name = f'{field}_{lang_code}'
                widget = forms.Textarea if field in ['description', 'meta_description'] else forms.TextInput
                self.declared_fields[field_name] = forms.CharField(
                    required=False,
                    widget=widget(),
                    label=f"{field.replace('_', ' ').title()} ({lang_code.upper()})"
                )
                setattr(self, field_name, self.declared_fields[field_name])

        super().__init__(*args, **kwargs)

        # Загружаем существующие переводы
        if self.instance.pk:
            translations = {t.language_code: t for t in self.instance.translations.all()}
            for lang_code, _ in settings.LANGUAGES:
                translation = translations.get(lang_code)
                if translation:
                    for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                        field_name = f'{field}_{lang_code}'
                        self.initial[field_name] = getattr(translation, field, '')

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            for lang_code, _ in settings.LANGUAGES:
                translation_data = {}
                for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                    field_name = f'{field}_{lang_code}'
                    if field_name in self.cleaned_data:
                        translation_data[field] = self.cleaned_data[field_name]

                if any(translation_data.values()):
                    ExtensionTranslation.objects.update_or_create(
                        extension=instance,
                        language_code=lang_code,
                        defaults=translation_data
                    )
        return instance


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionAdminForm

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

        # Группы переводимых полей
        translatable_fields = [
            ('Название', 'name'),
            ('Заголовок', 'title'),
            ('Краткое описание', 'short_description'),
            ('Описание', 'description'),
            ('Мета-описание', 'meta_description')
        ]

        for field_label, field_name in translatable_fields:
            translation_fields = []
            for lang_code, _ in settings.LANGUAGES:
                translation_fields.append(f'{field_name}_{lang_code}')

            fieldsets.append((
                field_label,
                {
                    'fields': translation_fields,
                    'classes': ('collapse',)
                }
            ))

        return fieldsets

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        # Добавляем все поля переводов в form.base_fields
        for lang_code, _ in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_name = f'{field}_{lang_code}'
                if field_name not in form.base_fields:
                    widget = forms.Textarea if field in ['description', 'meta_description'] else forms.TextInput
                    form.base_fields[field_name] = forms.CharField(
                        required=False,
                        widget=widget(),
                        label=f"{field.replace('_', ' ').title()} ({lang_code.upper()})"
                    )
        return form