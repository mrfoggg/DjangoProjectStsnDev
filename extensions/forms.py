from django import forms
from django.forms import TextInput, Textarea
from .models import ExtensionProxy
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget


class ExtensionProxyForm(forms.ModelForm):
    class Meta:
        model = ExtensionProxy
        fields = ['name', 'version', 'secret_key', 'trial_period_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Динамически добавляем поля для всех языков
        for lang in self.Meta.model.languages:
            name_field = f'name_{lang}'
            description_field = f'description_{lang}'

            # Добавляем поля формы с начальными значениями
            self.fields[name_field] = forms.CharField(
                label=lang.upper(),
                required=False,
                widget=UnfoldAdminTextInputWidget if lang == 'en' else UnfoldAdminTextInputWidget
            )
            self.fields[description_field] = forms.CharField(
                label=lang.upper(),
                required=False,
                widget=WysiwygWidget if lang == 'en' else WysiwygWidget
            )

            # Инициализация полей для существующего экземпляра
            if instance:
                translation = instance.get_translation(lang)
                if translation:
                    self.fields[name_field].initial = getattr(translation, 'name', '')
                    self.fields[description_field].initial = getattr(translation, 'description', '')

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Динамически сохраняем переводы для каждого языка и поля
        for lang in self.Meta.model.languages:
            instance.set_translation(lang, 'name', self.cleaned_data.get(f'name_{lang}'))
            instance.set_translation(lang, 'description', self.cleaned_data.get(f'description_{lang}'))

        if commit:
            instance.save()
        return instance
