from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation
from rich import print

class ExtensionAdminForm(forms.ModelForm):
    """
    Форма редактирования Extension с динамическими полями переводов
    (на втором этапе рендеринга).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:  # Только если это не новая запись
            translations = ExtensionTranslation.objects.filter(extension=self.instance)
            # print('DEBUG translations -', translations)
            existing_langs = {t.language_code for t in translations}

            from DjangoProjectStsnDev import settings  # Получаем список доступных языков
            for lang_code, lang_name in settings.LANGUAGES:
                # Если перевода нет — создаем пустую запись
                if lang_code not in existing_langs:
                    ExtensionTranslation.objects.create(extension=self.instance, language_code=lang_code)

            # После создания/обновления записей заново получаем переводы
            translations = ExtensionTranslation.objects.filter(extension=self.instance)

            for translation in translations:
                lang_code = translation.language_code

                self.fields[f'name_{lang_code}'] = forms.CharField(
                    initial=translation.name,
                    label=_('Name') + f" ({lang_code})",
                    max_length=255,
                    required=False
                )

                self.fields[f'description_{lang_code}'] = forms.CharField(
                    initial=translation.description,
                    label=_('Description') + f" ({lang_code})",
                    widget=forms.Textarea,
                    required=False
                )

                self.fields[f'short_description_{lang_code}'] = forms.CharField(
                    initial=translation.short_description,
                    label=_('Short Description') + f" ({lang_code})",
                    max_length=255,
                    required=False
                )

                self.fields[f'title_{lang_code}'] = forms.CharField(
                    initial=translation.title,
                    label=_('Title') + f" ({lang_code})",
                    max_length=255,
                    required=False
                )

                self.fields[f'meta_description_{lang_code}'] = forms.CharField(
                    initial=translation.meta_description,
                    label=_('Meta Description') + f" ({lang_code})",
                    widget=forms.Textarea,
                    required=False
                )
            # print('DEBUG fields - ', self.fields)
    class Meta:
        model = Extension
        fields = '__all__'
