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
        self.translation_fields = {}

        if self.instance.pk:
            self._create_translation_fields()

    def _create_translation_fields(self):
        for lang_code, lang_name in settings.LANGUAGES:
            translation = self._get_translation(lang_code)
            for field in ExtensionTranslation.get_translatable_fields():
                self._add_field(lang_code, lang_name, field, translation)

    def _get_translation(self, lang_code):
        try:
            return self.instance.translations.get(language_code=lang_code)
        except ExtensionTranslation.DoesNotExist:
            return ExtensionTranslation(
                extension=self.instance,
                language_code=lang_code
            )

    def _add_field(self, lang_code, lang_name, field_name, translation):
        field_id = f"trans_{field_name}_{lang_code}"
        self.fields[field_id] = forms.CharField(
            label=f"{ExtensionTranslation._meta.get_field(field_name).verbose_name} ({lang_name})",
            initial=getattr(translation, field_name, ''),
            required=False,
            widget=forms.Textarea if field_name == 'description' else forms.TextInput
        )
        self.translation_fields[field_id] = (lang_code, field_name)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self._save_translations(instance)
        return instance

    def _save_translations(self, instance):
        for field_id, (lang_code, field_name) in self.translation_fields.items():
            value = self.cleaned_data.get(field_id, '')
            ExtensionTranslation.objects.update_or_create(
                extension=instance,
                language_code=lang_code,
                defaults={field_name: value}
            )


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_fields(self, request, obj=None):
        return ['name', 'version', 'file', 'secret_key', 'trial_period_days']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {'fields': self.get_fields(request, obj)}),
        ]

        if obj and obj.pk:
            for lang_code, lang_name in settings.LANGUAGES:
                lang_fields = [
                    f"trans_{field}_{lang_code}"
                    for field in ExtensionTranslation.get_translatable_fields()
                ]
                fieldsets.append((
                    f"{lang_name} Translation",
                    {'fields': lang_fields, 'classes': ('collapse',)}
                ))

        return fieldsets

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('translations')

