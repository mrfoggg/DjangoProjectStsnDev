from django import forms
from django.forms import TextInput, Textarea
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget
from django.utils.translation import get_language

class ExtensionProxyFormMeta(type(forms.ModelForm)):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in ExtensionProxy.LANGUAGE_CHOICES]

        for field in translatable_fields:
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                label = lang_code.upper()
                widget = WysiwygWidget if field in ['description', 'short_description', 'meta_description'] else UnfoldAdminTextInputWidget

                new_class.base_fields[field_name] = forms.CharField(
                    label=label,
                    required=False,
                    widget=widget
                )

        return new_class

class ExtensionProxyForm(forms.ModelForm, metaclass=ExtensionProxyFormMeta):
    class Meta:
        model = ExtensionProxy
        fields = ['name', 'version', 'secret_key', 'trial_period_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            translatable_fields = ExtensionTranslation.get_translatable_fields()
            language_codes = [code for code, _ in ExtensionProxy.LANGUAGE_CHOICES]

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
        language_codes = [code for code, _ in ExtensionProxy.LANGUAGE_CHOICES]

        for field in translatable_fields:
            for lang_code in language_codes:
                field_name = f"{field}_{lang_code}"
                value = self.cleaned_data.get(field_name)
                if value:
                    instance.set_translation(lang_code, field, value)

        return instance
