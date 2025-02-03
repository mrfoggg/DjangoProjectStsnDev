# admin.py
from django import forms
from django.contrib import admin
from django.utils.module_loading import import_string
from unfold.admin import ModelAdmin

from DjangoProjectStsnDev import settings
from .models import Extension, ExtensionTranslation


class TranslationFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_translation_fields()

    def _add_translation_fields(self):
        for lang_code, lang_name in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                self._add_translation_field(lang_code, field)

    def _add_translation_field(self, lang_code, field_name):
        widget_class = import_string(self.Meta.widgets.get(field_name, 'django.forms.TextInput'))
        self.fields[f'{field_name}_{lang_code}'] = forms.CharField(
            label=f"{ExtensionTranslation._meta.get_field(field_name).verbose_name} ({lang_code.upper()})",
            required=False,
            widget=widget_class()
        )


class ExtensionAdminForm(TranslationFormMixin, forms.ModelForm):
    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'file']
        widgets = {
            'description': 'django.forms.Textarea',
            'meta_description': 'unfold.contrib.forms.widgets.WysiwygWidget'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self._init_translations()

    def _init_translations(self):
        translations = {t.language_code: t for t in self.instance.translations.all()}
        for lang_code, _ in settings.LANGUAGES:
            translation = translations.get(lang_code)
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                self.fields[f'{field}_{lang_code}'].initial = getattr(translation, field, '') if translation else ''

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self._save_translations(instance)
        return instance

    def _save_translations(self, instance):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {}
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                trans_data[field] = self.cleaned_data.get(f'{field}_{lang_code}', '')

            ExtensionTranslation.objects.update_or_create(
                extension=instance,
                language_code=lang_code,
                defaults=trans_data
            )


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ['name', 'version', 'secret_key', 'trial_period_days', 'file']
            }),
        ]

        # Динамически создаем секции для переводов
        for field_group in [
            ('Название', 'name'),
            ('Заголовок', 'title'),
            ('Краткое описание', 'short_description'),
            ('Полное описание', 'description'),
            ('Мета описание', 'meta_description')
        ]:
            section = []
            for lang_code, lang_name in settings.LANGUAGES:
                section.append(f'{field_group[1]}_{lang_code}')

            fieldsets.append((
                field_group[0],
                {
                    'fields': section,
                    'classes': ('collapse',)
                }
            ))

        return fieldsets