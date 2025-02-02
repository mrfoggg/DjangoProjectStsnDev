from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionForm(forms.Form):
    # Основные поля модели Extension
    name = forms.CharField(label=_('Name'), max_length=255)
    version = forms.CharField(label=_('Version'), max_length=50, required=False)
    secret_key = forms.CharField(label=_('Secret Key'), max_length=255)
    trial_period_days = forms.IntegerField(label=_('Trial Period (days)'), initial=30)

    def __init__(self, *args, **kwargs):
        self.extension = kwargs.pop('extension', None)
        super().__init__(*args, **kwargs)
        self._init_translation_fields()

    def _init_translation_fields(self):
        if not self.extension:
            return

        # Добавляем поля переводов для каждого языка
        for lang_code, lang_name in settings.LANGUAGES:
            translation = self._get_translation(lang_code)
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                self._add_translation_field(lang_code, lang_name, field, translation)

    def _get_translation(self, lang_code):
        try:
            return self.extension.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            return ExtensionTranslation(
                extension=self.extension,
                language_code=lang_code
            )

    def _add_translation_field(self, lang_code, lang_name, field_name, translation):
        field_id = f"{field_name}_{lang_code}"
        self.fields[field_id] = forms.CharField(
            label=f"{ExtensionTranslation._meta.get_field(field_name).verbose_name} ({lang_name})",
            initial=getattr(translation, field_name, ''),
            required=False,
            widget=forms.Textarea if field_name == 'description' else forms.TextInput
        )

    def save(self):
        # Сохраняем/обновляем основную модель
        extension = self.extension or Extension()
        extension.name = self.cleaned_data['name']
        extension.version = self.cleaned_data.get('version', '')
        extension.secret_key = self.cleaned_data['secret_key']
        extension.trial_period_days = self.cleaned_data['trial_period_days']
        extension.save()

        # Сохраняем переводы
        self._save_translations(extension)
        return extension

    def _save_translations(self, extension):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {}
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_id = f"{field}_{lang_code}"
                trans_data[field] = self.cleaned_data.get(field_id, '')

            ExtensionTranslation.objects.update_or_create(
                extension=extension,
                language_code=lang_code,
                defaults=trans_data
            )


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionForm
    list_display = ('name', 'version', 'secret_key')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.extension = obj  # Передаем объект через кастомный атрибут
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': [
                    'name',
                    'version',
                    'secret_key',
                    'trial_period_days'
                ]
            }),
        ]

        if obj:
            for lang_code, lang_name in settings.LANGUAGES:
                lang_fields = [
                    f"name_{lang_code}",
                    f"title_{lang_code}",
                    f"short_description_{lang_code}",
                    f"description_{lang_code}",
                    f"meta_description_{lang_code}"
                ]
                fieldsets.append((
                    f"{lang_name} Translation",
                    {
                        'fields': lang_fields,
                        'classes': ('collapse',)
                    }
                ))

        return fieldsets

    def save_model(self, request, obj, form, change):
        # Объект сохраняется через форму
        form.save()