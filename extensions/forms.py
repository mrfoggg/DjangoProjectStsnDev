from django import forms
from django.db.models import CharField, TextField
from django.forms.models import ModelFormMetaclass
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget

class ExtensionProxyFormMeta(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        # Сначала собираем новые поля
        additional_fields = {}
        for model_field in ExtensionTranslation._meta.fields:
            if isinstance(model_field, (CharField, TextField)) and not hasattr(model_field, 'choices'):
                form_field = model_field.formfield()
                form_field_kwargs = form_field.__dict__.copy()
                for lang_code in [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]:
                    new_form_field = form_field.__class__(**form_field_kwargs)
                    field_name = f"{model_field.name}_{lang_code}"
                    additional_fields[field_name] = new_form_field

        # Добавляем новые поля в attrs (класс формы)
        attrs.update(additional_fields)

        # Обновляем Meta.fields с учётом новых динамически добавленных полей
        if 'Meta' in attrs:
            if hasattr(attrs['Meta'], 'fields'):
                attrs['Meta'].fields = list(attrs['Meta'].fields) + list(additional_fields.keys())
            else:
                attrs['Meta'].fields = list(additional_fields.keys())

        return new_class


class ExtensionProxyForm(forms.ModelForm, metaclass=ExtensionProxyFormMeta):
    class Meta:
        model = ExtensionProxy
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

            for field in ExtensionTranslation._meta.fields:
                if isinstance(field, (CharField, TextField)) and not hasattr(field, 'choices'):
                    for lang_code in language_codes:
                        field_name = f"{field.name}_{lang_code}"
                        translation = instance.get_translation(lang_code)
                        if translation:
                            self.fields[field_name].initial = getattr(translation, field.name)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()

        language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

        for field in ExtensionTranslation._meta.fields:
            if isinstance(field, (CharField, TextField)) and not hasattr(field, 'choices'):
                for lang_code in language_codes:
                    field_name = f"{field.name}_{lang_code}"
                    value = self.cleaned_data.get(field_name)
                    if value:
                        instance.set_translation(lang_code, field.name, value)

        return instance
