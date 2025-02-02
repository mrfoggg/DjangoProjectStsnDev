from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings

class ExtensionAdminForm(forms.ModelForm):
    """
    Форма редактирования Extension с динамическими полями переводов
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:  # Только если это не новая запись
            translations = ExtensionTranslation.objects.filter(extension=self.instance)
            existing_langs = {t.language_code for t in translations}

            for lang_code, lang_name in settings.LANGUAGES:
                # Если перевода нет — создаем пустую запись
                if lang_code not in existing_langs:
                    ExtensionTranslation.objects.create(extension=self.instance, language_code=lang_code)

                # Добавляем поля переводов
                self.fields[f'name_{lang_code}'] = forms.CharField(
                    initial=translations.filter(language_code=lang_code).first().name if translations.filter(language_code=lang_code).exists() else '',
                    label=f'Name ({lang_code})',
                    max_length=255,
                    required=False
                )

                self.fields[f'description_{lang_code}'] = forms.CharField(
                    initial=translations.filter(language_code=lang_code).first().description if translations.filter(language_code=lang_code).exists() else '',
                    label=f'Description ({lang_code})',
                    widget=forms.Textarea,
                    required=False
                )

                self.fields[f'short_description_{lang_code}'] = forms.CharField(
                    initial=translations.filter(language_code=lang_code).first().short_description if translations.filter(language_code=lang_code).exists() else '',
                    label=f'Short Description ({lang_code})',
                    max_length=255,
                    required=False
                )

                self.fields[f'title_{lang_code}'] = forms.CharField(
                    initial=translations.filter(language_code=lang_code).first().title if translations.filter(language_code=lang_code).exists() else '',
                    label=f'Title ({lang_code})',
                    max_length=255,
                    required=False
                )

                self.fields[f'meta_description_{lang_code}'] = forms.CharField(
                    initial=translations.filter(language_code=lang_code).first().meta_description if translations.filter(language_code=lang_code).exists() else '',
                    label=f'Meta Description ({lang_code})',
                    widget=forms.Textarea,
                    required=False
                )

    class Meta:
        model = Extension
        fields = '__all__'

