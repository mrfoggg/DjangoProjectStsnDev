from django import forms
from django.db.models import CharField, TextField
from django.forms import TextInput, Textarea
from .models import ExtensionProxy, ExtensionTranslation
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget

class ExtensionProxyForm(forms.ModelForm):
    class Meta:
        model = ExtensionProxy
        fields = ['name', 'version', 'secret_key', 'trial_period_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        language_codes = [code for code, _ in ExtensionTranslation.LANGUAGE_CHOICES]

        for field in ExtensionTranslation._meta.fields:
            if isinstance(field, (CharField, TextField)) and not hasattr(field, 'choices'):
                for lang_code in language_codes:
                    field_name = f"{field.name}_{lang_code}"
                    label = lang_code.upper()
                    widget = WysiwygWidget if field.name in ['description', 'short_description', 'meta_description'] else UnfoldAdminTextInputWidget

                    self.fields[field_name] = forms.CharField(
                        label=label,
                        required=False,
                        widget=widget
                    )

                    if instance:
                        translation = instance.get_translation(lang_code)
                        if translation:
                            self.fields[field_name].initial = getattr(translation, field.name)

        # Обновляем Meta.fields с учётом новых динамически добавленных полей
        self._meta.fields = list(self._meta.fields) + list(self.fields.keys())

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
