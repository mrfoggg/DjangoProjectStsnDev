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


class ExtensionAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Add translation fields dynamically
        for lang_code, _ in settings.LANGUAGES:
            for field_name in ExtensionTranslation.get_translatable_fields():
                field_key = f'{field_name}_{lang_code}'

                # Set appropriate widget based on field type
                widget = forms.Textarea if field_name in ['description', 'meta_description'] else forms.TextInput

                self.fields[field_key] = forms.CharField(
                    required=False,
                    widget=widget(),
                    label=f"{field_name.replace('_', ' ').title()} ({lang_code.upper()})"
                )

                # Set initial values if instance exists
                if instance:
                    try:
                        translation = instance.translations.get(language_code=lang_code)
                        self.fields[field_key].initial = getattr(translation, field_name, '')
                    except ExtensionTranslation.DoesNotExist:
                        pass

    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'file']


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_fieldsets(self, request, obj=None):
        # Base fieldset with model fields
        fieldsets = [
            (_('Basic Information'), {
                'fields': [
                    'name', 'version', 'secret_key',
                    'trial_period_days', 'file'
                ]
            })
        ]

        # Translation fieldsets
        translation_groups = {
            _('Names'): ['name'],
            _('Titles'): ['title'],
            _('Short Descriptions'): ['short_description'],
            _('Descriptions'): ['description'],
            _('Meta Descriptions'): ['meta_description']
        }

        for group_label, field_names in translation_groups.items():
            translation_fields = []
            for field_name in field_names:
                translation_fields.extend([
                    f'{field_name}_{lang_code}'
                    for lang_code, _ in settings.LANGUAGES
                ])

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

        # Save translations
        for lang_code, _ in settings.LANGUAGES:
            translation_data = {}

            for field_name in ExtensionTranslation.get_translatable_fields():
                trans_field_name = f'{field_name}_{lang_code}'
                value = form.cleaned_data.get(trans_field_name)
                if value is not None:  # Allow empty strings but not None
                    translation_data[field_name] = value

            if translation_data:
                ExtensionTranslation.objects.update_or_create(
                    extension=obj,
                    language_code=lang_code,
                    defaults=translation_data
                )
