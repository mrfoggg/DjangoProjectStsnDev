# forms.py
from django import forms
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget

from DjangoProjectStsnDev import settings
from .models import ExtensionProxy


class ExtensionProxyForm(forms.ModelForm):
    class Meta:
        model = ExtensionProxy
        fields = ['name', 'version', 'secret_key', 'trial_period_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_translation_fields()
        self._init_translations()

    def _create_translation_fields(self):
        for lang_code, lang_name in settings.LANGUAGES:
            for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                self._add_field(lang_code, field)

    def _add_field(self, lang_code, field_name):
        field_id = f"{field_name}_{lang_code}"
        self.fields[field_id] = forms.CharField(
            label=f"{field_name.capitalize()} ({lang_code.upper()})",
            required=False,
            widget=self._get_widget(field_name)
        )

    def _get_widget(self, field_name):
        return WysiwygWidget() if field_name in ['description', 'meta_description'] else UnfoldAdminTextInputWidget()

    def _init_translations(self):
        if self.instance.pk:
            for lang_code, _ in settings.LANGUAGES:
                if translation := self.instance.get_translation(lang_code):
                    for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
                        self.fields[f"{field}_{lang_code}"].initial = getattr(translation, field)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self._save_all_translations(instance)
        return instance

    def _save_all_translations(self, instance):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {
                field: self.cleaned_data.get(f"{field}_{lang_code}", "")
                for field in ['name', 'title', 'short_description', 'description', 'meta_description']
            }
            instance.set_translation(lang_code, trans_data)