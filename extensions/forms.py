from django import forms
from django.db.models import CharField
from django.db.models.fields import TextField
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget


class ExtensionProxyFormMeta(type(forms.ModelForm)):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        # Сначала собираем новые поля
        additional_fields = {}
        for model_filed in ExtensionTranslation._meta.fields:
            if isinstance(model_filed, (CharField, TextField)) and not hasattr(model_filed, 'choices'):
                form_field = model_filed.formfield()
                form_field_kwargs = form_field.__dict__.copy()
                for lang_code in [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]:
                    new_form_field = form_field.__class__(**form_field_kwargs)
                    field_name = f"{model_filed.name}_{lang_code}"
                    additional_fields[field_name] = new_form_field

        # Добавляем новые поля в attrs (класс формы)
        attrs.update(additional_fields)

        # Обновляем Meta.fields с учётом новых динамически добавленных полей
        if 'Meta' in attrs:
            if hasattr(attrs['Meta'], 'fields'):
                attrs['Meta'].fields.extend(additional_fields.keys())
            else:
                attrs['Meta'].fields = list(additional_fields.keys())

        return new_class


class ExtensionProxyForm(forms.ModelForm, metaclass=ExtensionProxyFormMeta):
# class ExtensionProxyForm(forms.ModelForm):
    name_en = forms.CharField(
        label="EN",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    description_en = forms.CharField(
        label="EN",
        required=False,
        widget=WysiwygWidget
    )
    short_description_en = forms.CharField(
        label="EN",
        required=False,
        widget=WysiwygWidget
    )
    title_en = forms.CharField(
        label="EN",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    meta_description_en = forms.CharField(
        label="EN",
        required=False,
        widget=WysiwygWidget
    )

    name_ru = forms.CharField(
        label="RU",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    description_ru = forms.CharField(
        label="RU",
        required=False,
        widget=WysiwygWidget
    )
    short_description_ru = forms.CharField(
        label="RU",
        required=False,
        widget=WysiwygWidget
    )
    title_ru = forms.CharField(
        label="RU",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    meta_description_ru = forms.CharField(
        label="RU",
        required=False,
        widget=WysiwygWidget
    )

    name_uk = forms.CharField(
        label="UA",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    description_uk = forms.CharField(
        label="UA",
        required=False,
        widget=WysiwygWidget
    )
    short_description_uk = forms.CharField(
        label="UA",
        required=False,
        widget=WysiwygWidget
    )
    title_uk = forms.CharField(
        label="UA",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    meta_description_uk = forms.CharField(
        label="UA",
        required=False,
        widget=WysiwygWidget
    )
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

