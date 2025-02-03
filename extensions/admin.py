# admin.py
from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from DjangoProjectStsnDev import settings
from .models import Extension, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget

class ExtensionAdminForm(forms.ModelForm):
    class Meta:
        model = Extension
        fields = ['name', 'version', 'secret_key', 'file', 'trial_period_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_translation_fields()
        self._init_translation_values()

    def _create_translation_fields(self):
        """Динамически создает поля для всех языков и всех переводимых полей"""
        for lang_code, lang_name in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                self._add_translation_field(lang_code, field)

    def _add_translation_field(self, lang_code, field_name):
        """Создает поле перевода с правильным виджетом"""
        field_id = f"{field_name}_{lang_code}"
        self.fields[field_id] = forms.CharField(
            label=f"{field_name.capitalize()} ({lang_code.upper()})",
            required=False,
            widget=self._get_widget(field_name)
        )

    def _get_widget(self, field_name):
        """Возвращает виджет в зависимости от типа поля"""
        return WysiwygWidget() if field_name in ['description', 'meta_description'] else forms.TextInput()

    def _init_translation_values(self):
        """Инициализирует значения для существующих переводов"""
        if self.instance and self.instance.pk:
            for translation in self.instance.translations.all():
                for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                    self.fields[f"{field}_{translation.language_code}"].initial = getattr(translation, field)

    def save(self, commit=True):
        """Сохраняет основную модель и все переводы"""
        instance = super().save(commit=commit)
        if commit:
            self._save_translations(instance)
        return instance

    def _save_translations(self, instance):
        """Сохраняет или обновляет переводы для всех языков"""
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {
                field: self.cleaned_data.get(f"{field}_{lang_code}", "")
                for field in ['name', 'title', 'short_description', 'description', 'meta_description']
            }
            ExtensionTranslation.objects.update_or_create(
                extension=instance,
                language_code=lang_code,
                defaults=trans_data
            )

@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'trial_period_days')

    def get_fieldsets(self, request, obj=None):
        """Динамически генерирует структуру полей"""
        fieldsets = [
            (None, {
                'fields': ['name', 'version', 'secret_key', 'file', 'trial_period_days']
            }),
        ]

        # Группировка по типам полей
        field_groups = {
            _('Name'): ['name'],
            _('Title'): ['title'],
            _('Short Description'): ['short_description'],
            _('Description'): ['description'],
            _('Meta Description'): ['meta_description']
        }

        for group_name, fields in field_groups.items():
            for lang_code, lang_name in settings.LANGUAGES:
                lang_fields = [f"{field}_{lang_code}" for field in fields]
                fieldsets.append((
                    f"{group_name} ({lang_code.upper()})",
                    {
                        'fields': lang_fields,
                        'classes': ('collapse',)
                    }
                ))

        return fieldsets