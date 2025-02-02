from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionAdminForm(forms.ModelForm):
    class Meta:
        model = Extension
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_translation_fields()

    def _create_translation_fields(self):
        if self.instance and self.instance.pk:
            for lang_code, lang_name in settings.LANGUAGES:
                translation = self._get_or_create_translation(lang_code)
                for field in ExtensionTranslation.get_translatable_fields():
                    self._add_translation_field(lang_code, lang_name, field, translation)

    def _get_or_create_translation(self, lang_code):
        try:
            return self.instance.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            return ExtensionTranslation(
                extension=self.instance,
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
        self.fields[field_id].translation_field = True  # Помечаем как поле перевода

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self._save_translations(instance)
        return instance

    def _save_translations(self, instance):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {}
            for field in ExtensionTranslation.get_translatable_fields():
                field_id = f"{field}_{lang_code}"
                trans_data[field] = self.cleaned_data.get(field_id, '')

            ExtensionTranslation.objects.update_or_create(
                extension=instance,
                language_code=lang_code,
                defaults=trans_data
            )


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_fields(self, request, obj=None):
        # Возвращаем только оригинальные поля модели Extension
        return ['name', 'version', 'file', 'secret_key', 'trial_period_days']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': self.get_fields(request, obj)
            }),
        ]

        if obj and obj.pk:
            for lang_code, lang_name in settings.LANGUAGES:
                lang_fields = [
                    f"{field}_{lang_code}"
                    for field in ExtensionTranslation.get_translatable_fields()
                ]

                fieldsets.append((
                    f"{lang_name} Translation",
                    {
                        'fields': lang_fields,
                        'classes': ('collapse',)
                    }
                ))

        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.pk:
            form.base_fields.update(form.declared_fields)
        return form

