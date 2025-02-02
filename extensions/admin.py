from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionAdminForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.extension_instance = kwargs.pop('extension_instance', None)
        super().__init__(*args, **kwargs)
        self._create_fields()

    def _create_fields(self):
        # Основные поля
        self._add_base_field('name', forms.CharField, _('Name'))
        self._add_base_field('version', forms.CharField, _('Version'), required=False)
        self._add_base_field('secret_key', forms.CharField, _('Secret Key'))
        self._add_base_field('trial_period_days', forms.IntegerField, _('Trial Period (days)'), initial=30)

        # Поля переводов
        if self.extension_instance and self.extension_instance.pk:
            for lang_code, lang_name in settings.LANGUAGES:
                self._create_translation_fields(lang_code, lang_name)

    def _add_base_field(self, field_name, field_class, label, **kwargs):
        initial = getattr(self.extension_instance, field_name, None) if self.extension_instance else None
        self.fields[field_name] = field_class(
            label=label,
            initial=initial,
            **kwargs
        )

    def _create_translation_fields(self, lang_code, lang_name):
        translation = self._get_translation(lang_code)
        for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
            self._add_translation_field(lang_code, lang_name, field, translation)

    def _get_translation(self, lang_code):
        try:
            return self.extension_instance.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            return ExtensionTranslation(
                extension=self.extension_instance,
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
        # Сохраняем основную модель
        extension = self.extension_instance or Extension()
        for field in ['name', 'version', 'secret_key', 'trial_period_days']:
            setattr(extension, field, self.cleaned_data[field])
        extension.save()

        # Сохраняем переводы
        if extension.pk:
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
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.extension_instance = obj  # Передаем объект через кастомный атрибут
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

        if obj and obj.pk:
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