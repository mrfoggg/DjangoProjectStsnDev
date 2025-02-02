from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionAdminForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.obj_id = kwargs.pop('obj_id', None)  # Получаем ID объекта
        super().__init__(*args, **kwargs)
        self._create_fields()

    def _create_fields(self):
        # Основные поля
        self._add_base_fields()

        # Поля переводов
        if self.obj_id:
            self._create_translation_fields()

    def _add_base_fields(self):
        base_fields = {
            'name': forms.CharField(label=_('Name')),
            'version': forms.CharField(label=_('Version'), required=False),
            'secret_key': forms.CharField(label=_('Secret Key')),
            'trial_period_days': forms.IntegerField(label=_('Trial Period (days)'), initial=30)
        }

        # Для существующего объекта
        if self.obj_id:
            try:
                obj = Extension.objects.get(pk=self.obj_id)
                for field, form_field in base_fields.items():
                    form_field.initial = getattr(obj, field)
            except Extension.DoesNotExist:
                pass

        self.fields.update(base_fields)

    def _create_translation_fields(self):
        obj = Extension.objects.get(pk=self.obj_id)
        for lang_code, lang_name in settings.LANGUAGES:
            try:
                translation = obj.translations.get(language_code=lang_code)
            except ExtensionTranslation.DoesNotExist:
                translation = ExtensionTranslation(
                    extension=obj,
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
        obj_data = {
            'name': self.cleaned_data['name'],
            'version': self.cleaned_data['version'],
            'secret_key': self.cleaned_data['secret_key'],
            'trial_period_days': self.cleaned_data['trial_period_days']
        }

        if self.obj_id:
            obj = Extension.objects.get(pk=self.obj_id)
            for key, value in obj_data.items():
                setattr(obj, key, value)
            obj.save()
        else:
            obj = Extension.objects.create(**obj_data)

        # Сохраняем переводы
        self._save_translations(obj)
        return obj

    def _save_translations(self, obj):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {}
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_id = f"{field}_{lang_code}"
                trans_data[field] = self.cleaned_data.get(field_id, '')

            ExtensionTranslation.objects.update_or_create(
                extension=obj,
                language_code=lang_code,
                defaults=trans_data
            )


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.obj_id = obj.pk  # Передаем ID объекта в форму
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