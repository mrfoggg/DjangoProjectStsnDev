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
            self.fields['name_en'].initial = instance.get_translation('en').name if instance.get_translation('en') else ''
            self.fields['description_en'].initial = instance.get_translation('en').description if instance.get_translation('en') else ''
            self.fields['short_description_en'].initial = instance.get_translation('en').short_description if instance.get_translation('en') else ''
            self.fields['title_en'].initial = instance.get_translation('en').title if instance.get_translation('en') else ''
            self.fields['meta_description_en'].initial = instance.get_translation('en').meta_description if instance.get_translation('en') else ''

            self.fields['name_ru'].initial = instance.get_translation('ru').name if instance.get_translation('ru') else ''
            self.fields['description_ru'].initial = instance.get_translation('ru').description if instance.get_translation('ru') else ''
            self.fields['short_description_ru'].initial = instance.get_translation('ru').short_description if instance.get_translation('ru') else ''
            self.fields['title_ru'].initial = instance.get_translation('ru').title if instance.get_translation('ru') else ''
            self.fields['meta_description_ru'].initial = instance.get_translation('ru').meta_description if instance.get_translation('ru') else ''

            self.fields['name_uk'].initial = instance.get_translation('uk').name if instance.get_translation('uk') else ''
            self.fields['description_uk'].initial = instance.get_translation('uk').description if instance.get_translation('uk') else ''
            self.fields['short_description_uk'].initial = instance.get_translation('uk').short_description if instance.get_translation('uk') else ''
            self.fields['title_uk'].initial = instance.get_translation('ua').title if instance.get_translation('uk') else ''
            self.fields['meta_description_uk'].initial = instance.get_translation('uk').meta_description if instance.get_translation('uk') else ''

    def save(self, commit=True):
        # Сначала сохраняем основную модель Extension
        instance = super().save(commit=False)

        # Сохраняем основную модель, если commit=True
        # if commit:
        instance.save()

        # Теперь выполняем сохранение переводов
        instance.set_translation('en', 'name', self.cleaned_data['name_en'])
        instance.set_translation('en', 'description', self.cleaned_data['description_en'])
        instance.set_translation('en', 'short_description', self.cleaned_data['short_description_en'])
        instance.set_translation('en', 'title', self.cleaned_data['title_en'])
        instance.set_translation('en', 'meta_description', self.cleaned_data['meta_description_en'])

        instance.set_translation('ru', 'name', self.cleaned_data['name_ru'])
        instance.set_translation('ru', 'description', self.cleaned_data['description_ru'])
        instance.set_translation('ru', 'short_description', self.cleaned_data['short_description_ru'])
        instance.set_translation('ru', 'title', self.cleaned_data['title_ru'])
        instance.set_translation('ru', 'meta_description', self.cleaned_data['meta_description_ru'])

        instance.set_translation('uk', 'name', self.cleaned_data['name_uk'])
        instance.set_translation('uk', 'description', self.cleaned_data['description_uk'])
        instance.set_translation('uk', 'short_description', self.cleaned_data['short_description_uk'])
        instance.set_translation('uk', 'title', self.cleaned_data['title_uk'])
        instance.set_translation('uk', 'meta_description', self.cleaned_data['meta_description_uk'])

        return instance