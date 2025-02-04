from django import forms
from django.db import models
from django.db.models import CharField, TextField
from django.forms.models import ModelFormMetaclass
from DjangoProjectStsnDev import settings
from .models import ExtensionTranslation, Extension
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget


class CustomModelFormMeta(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        for model_field in ExtensionTranslation.get_translatable_fields():
            for lang_code, _ in settings.LANGUAGES:
                field_name = f"{model_field.name}_{lang_code}"
                form_field = model_field.formfield()
                if isinstance(model_field, models.CharField):
                    form_field.widget = UnfoldAdminTextInputWidget()
                elif isinstance(model_field, models.TextField):
                    form_field.widget = WysiwygWidget()
                form_field.label = lang_code

                new_class.declared_fields[field_name] = form_field

        return new_class

class ExtensionForm(forms.ModelForm, metaclass=CustomModelFormMeta):
    class Meta:
        model = Extension  # Используем основную модель
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            language_codes = [code for code, _ in settings.LANGUAGES]
            for field in ExtensionTranslation.get_translatable_fields():
                if isinstance(field, (CharField, TextField)) and not hasattr(field, 'choices'):
                    for lang_code in language_codes:
                        field_name = f"{field.name}_{lang_code}"
                        translation = instance.current_lang_translation
                        if translation:
                            self.fields[field_name].initial = getattr(translation, field.name)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        language_codes = [code for code, _ in settings.LANGUAGES]

        for field in ExtensionTranslation._meta.fields:
            if isinstance(field, (CharField, TextField)) and not hasattr(field, 'choices'):
                for lang_code in language_codes:
                    field_name = f"{field.name}_{lang_code}"
                    value = self.cleaned_data.get(field_name)
                    if value:
                        instance.set_translation(lang_code, field.name, value)

        return instance
