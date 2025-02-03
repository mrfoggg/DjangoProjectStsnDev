from django import forms
from django.db.models import CharField
from django.db.models.fields import TextField
from django.forms import TextInput, Textarea
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget

class ExtensionProxyFormMeta(type(forms.ModelForm)):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        for model_filed in ExtensionTranslation._meta.fields:
            if isinstance(model_filed, (CharField, TextField)) and not hasattr(model_filed, 'choices'):
                form_field = model_filed.formfield()
                form_field_kwargs = form_field.__dict__.copy()
                for lang_code in [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]:
                    new_form_field = form_field.__class__(**form_field_kwargs)
                    field_name = f"{model_filed.name}_{lang_code}"
                    setattr(ExtensionProxyFormMeta, field_name, new_form_field)
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

