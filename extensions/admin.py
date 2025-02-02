from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionAdminForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.obj = kwargs.pop('obj', None)  # Основной объект
        super().__init__(*args, **kwargs)
        self._create_fields()
        self.instance = self.obj  # Эмулируем поведение ModelForm

    def _create_fields(self):
        # Основные поля
        self.fields['name'] = forms.CharField(
            label=_('Name'),
            initial=self.obj.name if self.obj else ''
        )
        self.fields['version'] = forms.CharField(
            label=_('Version'),
            required=False,
            initial=self.obj.version if self.obj else ''
        )
        self.fields['secret_key'] = forms.CharField(
            label=_('Secret Key'),
            initial=self.obj.secret_key if self.obj else ''
        )
        self.fields['trial_period_days'] = forms.IntegerField(
            label=_('Trial Period (days)'),
            initial=self.obj.trial_period_days if self.obj else 30
        )

        # Поля переводов (только для существующих объектов)
        if self.obj and self.obj.pk:
            for lang_code, lang_name in settings.LANGUAGES:
                self._add_translation_fields(lang_code, lang_name)

    def _add_translation_fields(self, lang_code, lang_name):
        try:
            translation = self.obj.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            translation = ExtensionTranslation(
                extension=self.obj,
                language_code=lang_code
            )

        for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
            self._add_translation_field(lang_code, lang_name, field, translation)

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
        if self.obj:
            self.obj.name = self.cleaned_data['name']
            self.obj.version = self.cleaned_data['version']
            self.obj.secret_key = self.cleaned_data['secret_key']
            self.obj.trial_period_days = self.cleaned_data['trial_period_days']
            self.obj.save()
        else:
            self.obj = Extension.objects.create(
                name=self.cleaned_data['name'],
                version=self.cleaned_data['version'],
                secret_key=self.cleaned_data['secret_key'],
                trial_period_days=self.cleaned_data['trial_period_days']
            )

        # Сохраняем переводы
        self._save_translations()
        return self.obj

    def _save_translations(self):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {}
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_id = f"{field}_{lang_code}"
                trans_data[field] = self.cleaned_data.get(field_id, '')

            ExtensionTranslation.objects.update_or_create(
                extension=self.obj,
                language_code=lang_code,
                defaults=trans_data
            )


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.obj = obj  # Передаем объект в форму
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
        # Обновляем объект из формы
        obj = form.save()
        return obj