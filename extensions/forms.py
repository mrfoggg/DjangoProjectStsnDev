from django import forms
from django.forms import TextInput, Textarea
from .models import ExtensionProxy
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget


class ExtensionProxyForm(forms.ModelForm):
    class Meta:
        model = ExtensionProxy
        fields = ['version', 'secret_key', 'trial_period_days']  # Основные поля модели без переводов

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        # Динамически добавляем поля для каждого языка и атрибута
        for lang in self.Meta.model.languages:
            for attr in self.Meta.model.attributes:
                field_name = f'{attr}_{lang}'

                # Добавляем поля формы с начальными значениями
                self.fields[field_name] = forms.CharField(
                    label=lang.upper(),
                    required=False,
                    widget=WysiwygWidget if attr == 'description' else UnfoldAdminTextInputWidget
                )

                # Инициализация полей для существующего экземпляра
                if instance:
                    initial_value = getattr(instance, f'{attr}_{lang}', '')
                    self.fields[field_name].initial = initial_value

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Динамически сохраняем переводы для каждого языка и атрибута
        for lang in self.Meta.model.languages:
            for attr in self.Meta.model.attributes:
                value = self.cleaned_data.get(f'{attr}_{lang}')
                # Устанавливаем значения для каждого языка и атрибута
                instance.set_translation(lang, attr, value)

        if commit:
            instance.save()
        return instance
