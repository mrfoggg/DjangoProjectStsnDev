from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionForm(forms.Form):
    # Основные поля модели Extension
    name = forms.CharField(label=_('Name'), max_length=255)
    version = forms.CharField(label=_('Version'), required=False, max_length=50)
    secret_key = forms.CharField(label=_('Secret Key'), max_length=255)
    trial_period_days = forms.IntegerField(label=_('Trial Period (days)'), initial=30)

    def __init__(self, *args, **kwargs):
        self.extension = kwargs.pop('extension', None)
        super().__init__(*args, **kwargs)

        # Инициализируем основные поля
        if self.extension:
            self._init_base_fields()
            self._init_translation_fields()

    def _init_base_fields(self):
        self.fields['name'].initial = self.extension.name
        self.fields['version'].initial = self.extension.version
        self.fields['secret_key'].initial = self.extension.secret_key
        self.fields['trial_period_days'].initial = self.extension.trial_period_days

    def _init_translation_fields(self):
        # Добавляем поля переводов для каждого языка
        for lang_code, lang_name in settings.LANGUAGES:
            self._add_language_fields(lang_code, lang_name)

    def _add_language_fields(self, lang_code, lang_name):
        # Получаем или создаем перевод
        try:
            translation = self.extension.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            translation = ExtensionTranslation(
                extension=self.extension,
                language_code=lang_code
            )

        # Создаем поля для каждого переводимого атрибута
        for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
            self._create_translation_field(field, lang_code, lang_name, translation)

    def _create_translation_field(self, field_name, lang_code, lang_name, translation):
        field_id = f"{field_name}_{lang_code}"
        self.fields[field_id] = forms.CharField(
            label=f"{ExtensionTranslation._meta.get_field(field_name).verbose_name} ({lang_name})",
            initial=getattr(translation, field_name, ''),
            required=False,
            widget=self._get_widget_for_field(field_name)
        )

    def _get_widget_for_field(self, field_name):
        return forms.Textarea if field_name == 'description' else forms.TextInput

    def save(self):
        # Сохраняем основную модель
        extension = self.extension or Extension()
        extension.name = self.cleaned_data['name']
        extension.version = self.cleaned_data['version']
        extension.secret_key = self.cleaned_data['secret_key']
        extension.trial_period_days = self.cleaned_data['trial_period_days']
        extension.save()

        # Сохраняем переводы
        self._save_translations(extension)
        return extension

    def _save_translations(self, extension):
        for lang_code, _ in settings.LANGUAGES:
            self._save_language_translation(extension, lang_code)

    def _save_language_translation(self, extension, lang_code):
        trans_data = {
            'name': self.cleaned_data.get(f'name_{lang_code}', ''),
            'title': self.cleaned_data.get(f'title_{lang_code}', ''),
            'short_description': self.cleaned_data.get(f'short_description_{lang_code}', ''),
            'description': self.cleaned_data.get(f'description_{lang_code}', ''),
            'meta_description': self.cleaned_data.get(f'meta_description_{lang_code}', '')
        }

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
        kwargs['extension'] = obj
        return super().get_form(request, obj, **kwargs)

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
        # Сохранение полностью делегируем форме
        form.save()