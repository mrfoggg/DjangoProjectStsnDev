from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionAdminForm(forms.Form):
    # Основные поля
    name = forms.CharField(label=_('Name'), max_length=255)
    version = forms.CharField(label=_('Version'), max_length=50, required=False)
    secret_key = forms.CharField(label=_('Secret Key'), max_length=255)
    trial_period_days = forms.IntegerField(label=_('Trial Period (days)'), initial=30)

    def __init__(self, *args, **kwargs):
        self.extension = None  # Будет установлено позже
        super().__init__(*args, **kwargs)
        self._init_fields(self)

    def _init_fields(self):
        if self.extension:
            self._init_existing_fields()
            self._add_translation_fields()

    def _init_existing_fields(self):
        self.fields['name'].initial = self.extension.name
        self.fields['version'].initial = self.extension.version
        self.fields['secret_key'].initial = self.extension.secret_key
        self.fields['trial_period_days'].initial = self.extension.trial_period_days

    def _add_translation_fields(self):
        for lang_code, lang_name in settings.LANGUAGES:
            translation = self._get_translation(lang_code)
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                self._add_translation_field(field, lang_code, lang_name, translation)

    def _get_translation(self, lang_code):
        try:
            return self.extension.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            return ExtensionTranslation(
                extension=self.extension,
                language_code=lang_code
            )

    def _add_translation_field(self, field_name, lang_code, lang_name, translation):
        field_id = f"{field_name}_{lang_code}"
        self.fields[field_id] = forms.CharField(
            label=f"{ExtensionTranslation._meta.get_field(field_name).verbose_name} ({lang_name})",
            initial=getattr(translation, field_name, ''),
            required=False,
            widget=forms.Textarea if field_name == 'description' else forms.TextInput
        )

    def save(self):
        extension = self.extension or Extension()
        extension.name = self.cleaned_data['name']
        extension.version = self.cleaned_data['version']
        extension.secret_key = self.cleaned_data['secret_key']
        extension.trial_period_days = self.cleaned_data['trial_period_days']
        extension.save()

        for lang_code, _ in settings.LANGUAGES:
            self._save_translation(extension, lang_code)

        return extension

    def _save_translation(self, extension, lang_code):
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
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.extension = obj  # Устанавливаем объект после создания формы
        form._init_fields()  # Вызываем инициализацию полей
        return form

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ['name', 'version', 'secret_key', 'trial_period_days']
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
                    {'fields': lang_fields, 'classes': ('collapse',)}
                ))

        return fieldsets

    def save_model(self, request, obj, form, change):
        form.save()