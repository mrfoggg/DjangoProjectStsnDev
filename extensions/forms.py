from django import forms
from django.forms import TextInput, Textarea
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget

class ExtensionProxyForm(forms.ModelForm):
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
