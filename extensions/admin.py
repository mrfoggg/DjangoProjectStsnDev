from django.contrib import admin
from django.template.context import Context
from extensions.models import Extension
from unfold.admin import ModelAdmin

# @admin.register(Extension)
# class ExtensionAdmin(ModelAdmin):  # Заменяем на стандартный ModelAdmin
#     list_display = ['name', 'file_id']
#     fields = [('name', 'version'), ('file_id', 'secret_key'), ('file', 'trial_period_days')]

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Extension, ExtensionTranslation

class ExtensionAdminForm(forms.ModelForm):
    """
    Кастомная форма для модели Extension, в которую добавляются
    поля для языковых переводов.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            translations = ExtensionTranslation.objects.filter(extension=self.instance)
            for translation in translations:
                # Динамически добавляем поля в форму для каждого языка
                lang_code = translation.language_code

                self.fields[f'name_{lang_code}'] = forms.CharField(
                    initial=translation.name,
                    label=_('Name') + f" ({lang_code})",
                    max_length=255,
                    required=False
                )

                self.fields[f'description_{lang_code}'] = forms.CharField(
                    initial=translation.description,
                    label=_('Description') + f" ({lang_code})",
                    widget=forms.Textarea,
                    required=False
                )

                self.fields[f'short_description_{lang_code}'] = forms.CharField(
                    initial=translation.short_description,
                    label=_('Short Description') + f" ({lang_code})",
                    max_length=255,
                    required=False
                )

                self.fields[f'title_{lang_code}'] = forms.CharField(
                    initial=translation.title,
                    label=_('Title') + f" ({lang_code})",
                    max_length=255,
                    required=False
                )

                self.fields[f'meta_description_{lang_code}'] = forms.CharField(
                    initial=translation.meta_description,
                    label=_('Meta Description') + f" ({lang_code})",
                    widget=forms.Textarea,
                    required=False
                )

    class Meta:
        model = Extension
        fields = '__all__'


class ExtensionAdmin(admin.ModelAdmin):
    """
    Кастомный ModelAdmin для модели Extension,
    который добавляет редактирование переводов без инлайнов.
    """
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def save_model(self, request, obj, form, change):
        """
        Переопределяем сохранение модели, чтобы обработать сохранение переводов.
        """
        super().save_model(request, obj, form, change)

        for field_name, value in form.cleaned_data.items():
            if "_" in field_name:
                field, lang_code = field_name.rsplit("_", 1)
                translation, created = ExtensionTranslation.objects.get_or_create(
                    extension=obj, language_code=lang_code
                )
                setattr(translation, field, value)
                translation.save()


admin.site.register(Extension, ExtensionAdmin)


