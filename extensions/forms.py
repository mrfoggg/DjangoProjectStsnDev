from django import forms
from django.db import models
# from django.db.models import CharField, TextField
from django.forms.models import ModelFormMetaclass
from DjangoProjectStsnDev import settings
from .models import ExtensionTranslation, Extension
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminTextareaWidget, UnfoldAdminExpandableTextareaWidget


class CustomModelFormMeta(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        for model_field in ExtensionTranslation.get_translatable_fields():
            for lang_code, _ in settings.LANGUAGES:
                field_name = f"{model_field.name}_{lang_code}"
                form_field = model_field.formfield()
                if isinstance(model_field, models.CharField):
                    form_field.widget = UnfoldAdminTextInputWidget()
                elif isinstance(model_field, models.TextField):
                    if model_field.name in ExtensionTranslation.get_wysiwyg_widget_fields_list():
                        form_field.widget = WysiwygWidget()
                    else:
                        form_field.widget = UnfoldAdminExpandableTextareaWidget()
                form_field.label = lang_code

                new_class.declared_fields[field_name] = form_field

        return new_class

class ExtensionForm(forms.ModelForm, metaclass=CustomModelFormMeta):
    class Meta:
        model = Extension  # Используем основную модель
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.language_codes = [code for code, _ in settings.LANGUAGES]
            self.translation_fields = ExtensionTranslation.get_translatable_fields()

            for lang_code in self.language_codes:
                translation_instance = instance.get_translation(lang_code)
                for field in self.translation_fields:
                    translation_form_field_name = f"{field.name}_{lang_code}"
                    self.fields[translation_form_field_name].initial = getattr(translation_instance, field.name) if translation_instance else ""

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if 1:
            cleaned_data = self.cleaned_data
            for lang_code in [code for code, _ in settings.LANGUAGES]:
                ExtensionTranslation.objects.update_or_create(
                    extension=instance,
                    language_code=lang_code,
                    defaults={field.name: cleaned_data.get(f"{field.name}_{lang_code}", None) for field in
                              ExtensionTranslation.get_translatable_fields()}
                )
        return instance
