# admin.py
from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin

from DjangoProjectStsnDev import settings
from .models import ExtensionProxy
from unfold.contrib.forms.widgets import WysiwygWidget


class ExtensionProxyForm(forms.ModelForm):
    class Meta:
        model = ExtensionProxy
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Удаляем оригинальные поля модели
        self.fields.pop('name', None)
        self.fields.pop('translations', None)

        # Динамически добавляем поля переводов
        for lang_code, lang_name in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                field_name = f'{field}_{lang_code}'
                self.fields[field_name] = self._create_translation_field(field, lang_code)

    def _create_translation_field(self, field, lang_code):
        return forms.CharField(
            label=f"{field.capitalize()} ({lang_code.upper()})",
            required=False,
            widget=self._get_widget(field)
        )

    def _get_widget(self, field):
        return WysiwygWidget() if field in ['description', 'meta_description'] else forms.TextInput()


@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ['version', 'secret_key', 'trial_period_days', 'file']
            }),
        ]

        # Группировка по типам полей
        for field_type in [
            ('Name', 'name'),
            ('Title', 'title'),
            ('Short Description', 'short_description'),
            ('Description', 'description'),
            ('Meta Description', 'meta_description')
        ]:
            fields_group = []
            for lang_code, lang_name in settings.LANGUAGES:
                fields_group.append(f"{field_type[1]}_{lang_code}")

            fieldsets.append((
                field_type[0],
                {
                    'fields': fields_group,
                    'classes': ('collapse',)
                }
            ))

        return fieldsets