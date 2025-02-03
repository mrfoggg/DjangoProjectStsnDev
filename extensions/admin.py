# admin.py
from django import forms
from django.contrib import admin
from django.utils.module_loading import import_string
from unfold.admin import ModelAdmin
from django.utils.translation import gettext_lazy as _

from DjangoProjectStsnDev import settings
from extensions.models import ExtensionTranslation, Extension


class ExtensionAdminForm(forms.ModelForm):
    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'file']


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Словарь для хранения полей перевода
        translation_fields = {}

        for lang_code, _ in settings.LANGUAGES:
            for field_name in ['name', 'title', 'short_description', 'description', 'meta_description']:
                # Создаем имя поля перевода
                trans_field_name = f'{field_name}_{lang_code}'

                # Определяем виджет в зависимости от типа поля
                if field_name in ['description', 'meta_description']:
                    widget = forms.Textarea
                else:
                    widget = forms.TextInput

                # Создаем поле формы
                translation_fields[trans_field_name] = forms.CharField(
                    required=False,
                    widget=widget(),
                    label=f"{field_name.replace('_', ' ').title()} ({lang_code.upper()})"
                )

                # Добавляем начальные данные, если объект существует
                if obj:
                    try:
                        trans = obj.translations.get(language_code=lang_code)
                        translation_fields[trans_field_name].initial = getattr(trans, field_name, '')
                    except ExtensionTranslation.DoesNotExist:
                        pass

        # Добавляем поля в форму
        form.base_fields.update(translation_fields)

        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': [
                    'name', 'version', 'secret_key',
                    'trial_period_days', 'file'
                ]
            })
        ]

        # Группируем поля по типу (название, описание и т.д.)
        field_groups = [
            ('Название', 'name'),
            ('Заголовок', 'title'),
            ('Краткое описание', 'short_description'),
            ('Описание', 'description'),
            ('Мета-описание', 'meta_description')
        ]

        # Создаем группы полей для каждого типа перевода
        for group_label, field_name in field_groups:
            translation_fields = [
                f'{field_name}_{lang_code}'
                for lang_code, _ in settings.LANGUAGES
            ]
            fieldsets.append((
                group_label,
                {
                    'fields': translation_fields,
                    'classes': ('collapse',)
                }
            ))

        return fieldsets

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Сохраняем переводы
        for lang_code, _ in settings.LANGUAGES:
            translation_data = {}
            has_translation_data = False

            for field_name in ['name', 'title', 'short_description', 'description', 'meta_description']:
                trans_field_name = f'{field_name}_{lang_code}'
                value = form.cleaned_data.get(trans_field_name)
                if value:
                    translation_data[field_name] = value
                    has_translation_data = True

            if has_translation_data:
                ExtensionTranslation.objects.update_or_create(
                    extension=obj,
                    language_code=lang_code,
                    defaults=translation_data
                )