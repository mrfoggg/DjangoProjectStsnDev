# admin.py
from django import forms
from django.contrib import admin
from django.utils.module_loading import import_string
from unfold.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from DjangoProjectStsnDev import settings
from extensions.models import ExtensionTranslation, Extension


class ExtensionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем поля переводов до вызова родительского __init__
        for lang_code, _ in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_name = f'{field}_{lang_code}'
                # Определяем тип виджета в зависимости от поля
                widget = forms.Textarea if field in ['description', 'meta_description'] else forms.TextInput
                # Добавляем поле в форму
                self.fields[field_name] = forms.CharField(
                    required=False,
                    widget=widget(),
                    label=f"{field.replace('_', ' ').title()} ({lang_code.upper()})"
                )

        # Загружаем существующие переводы
        if self.instance.pk:
            translations = {
                t.language_code: t for t in self.instance.translations.all()
            }
            for lang_code, _ in settings.LANGUAGES:
                if translation := translations.get(lang_code):
                    for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                        field_name = f'{field}_{lang_code}'
                        if field_name in self.fields:
                            self.fields[field_name].initial = getattr(translation, field, '')

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            # Сохраняем переводы
            for lang_code, _ in settings.LANGUAGES:
                translation_data = {
                    field: self.cleaned_data.get(f'{field}_{lang_code}', '')
                    for field in ['name', 'title', 'short_description', 'description', 'meta_description']
                }
                ExtensionTranslation.objects.update_or_create(
                    extension=instance,
                    language_code=lang_code,
                    defaults=translation_data
                )
        return instance

    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'file']


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

        # Группы переводимых полей
        translatable_fields = [
            ('Название', 'name'),
            ('Заголовок', 'title'),
            ('Краткое описание', 'short_description'),
            ('Описание', 'description'),
            ('Мета-описание', 'meta_description')
        ]

        # Создаем группы полей для каждого переводимого поля
        for field_label, field_name in translatable_fields:
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