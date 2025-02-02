from django import forms
from .models import ExtensionProxy

class ExtensionProxyForm(forms.ModelForm):
    """Форма для работы с виртуальными полями в ExtensionProxy"""

    name_en = forms.CharField(
        label="Название (EN)",
        required=False,
        widget=forms.TextInput()
    )
    description_en = forms.CharField(
        label="Описание (EN)",
        required=False,
        widget=forms.Textarea()
    )
    name_ru = forms.CharField(
        label="Название (RU)",
        required=False,
        widget=forms.TextInput()
    )
    description_ru = forms.CharField(
        label="Описание (RU)",
        required=False,
        widget=forms.Textarea()
    )

    class Meta:
        model = ExtensionProxy
        fields = ['name', 'version', 'secret_key', 'trial_period_days']

    def __init__(self, *args, **kwargs):
        """Заполняем форму данными из модели"""
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['name_en'].initial = instance.name_en
            self.fields['description_en'].initial = instance.description_en
            self.fields['name_ru'].initial = instance.name_ru
            self.fields['description_ru'].initial = instance.description_ru

    def save(self, commit=True):
        """Сохраняем данные виртуальных полей"""
        instance = super().save(commit=False)
        instance.name_en = self.cleaned_data['name_en']
        instance.description_en = self.cleaned_data['description_en']
        instance.name_ru = self.cleaned_data['name_ru']
        instance.description_ru = self.cleaned_data['description_ru']
        if commit:
            instance.save()
        return instance
