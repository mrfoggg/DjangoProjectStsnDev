from django import forms
from django.db.models import CharField
from django.db.models.fields import TextField
from django.forms.models import ModelFormMetaclass

from DjangoProjectStsnDev import settings
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget
from rich import print


# class ExtensionProxyFormMeta(forms.models.ModelFormMetaclass):
class ExtensionProxyFormMeta(forms.models.ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        # Создаем форму через метакласс
        new_class = super().__new__(cls, name, bases, attrs)

        # Собираем новые поля
        additional_fields = {}
        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in settings.LANGUAGES]

        for field in translatable_fields:
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                field_instance = forms.CharField(label=field_name, required=False)
                additional_fields[field_name] = field_instance

        # Обновляем атрибуты класса, добавляя новые поля
        attrs.update(additional_fields)

        # Обновляем Meta.fields, чтобы включить новые поля
        if 'Meta' in attrs:
            if hasattr(attrs['Meta'], 'fields'):
                attrs['Meta'].fields.extend(additional_fields.keys())
            else:
                attrs['Meta'].fields = list(additional_fields.keys())

        return new_class


class ExtensionProxyForm(forms.ModelForm, metaclass=ExtensionProxyFormMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('DEBUF - self.fields - ', self.fields)
        instance = kwargs.get('instance')
        if instance:
            translatable_fields = ExtensionTranslation.get_translatable_fields()
            language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

            for field in translatable_fields:
                for lang_code in language_codes:
                    field_name = f"{field}_{lang_code}"
                    translation = instance.get_translation(lang_code)
                    if translation:
                        self.fields[field_name].initial = getattr(translation, field)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

        for field in translatable_fields:
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                value = self.cleaned_data.get(field_name)
                if value:
                    instance.set_translation(lang_code, field, value)

        return instance
