from django import forms
from django.forms import TextInput, Textarea
from .models import ExtensionProxy
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

    name_ua = forms.CharField(
        label="UA",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    description_ua = forms.CharField(
        label="UA",
        required=False,
        widget=WysiwygWidget
    )
    short_description_ua = forms.CharField(
        label="UA",
        required=False,
        widget=WysiwygWidget
    )
    title_ua = forms.CharField(
        label="UA",
        required=False,
        widget=UnfoldAdminTextInputWidget
    )
    meta_description_ua = forms.CharField(
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
            self.fields['name_en'].initial = instance.get_translation('en').name if instance.get_translation('en') else ''
            self.fields['description_en'].initial = instance.get_translation('en').description if instance.get_translation('en') else ''
            self.fields['name_ru'].initial = instance.get_translation('ru').name if instance.get_translation('ru') else ''
            self.fields['description_ru'].initial = instance.get_translation('ru').description if instance.get_translation('ru') else ''

    def save(self, commit=True):
        # Сначала сохраняем основную модель Extension
        instance = super().save(commit=False)

        # Сохраняем основную модель, если commit=True
        # if commit:
        instance.save()

        # Теперь выполняем сохранение переводов
        instance.set_translation('en', 'name', self.cleaned_data['name_en'])
        instance.set_translation('en', 'description', self.cleaned_data['description_en'])
        instance.set_translation('ru', 'name', self.cleaned_data['name_ru'])
        instance.set_translation('ru', 'description', self.cleaned_data['description_ru'])

        return instance
