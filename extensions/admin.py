from django import forms
from django.contrib import admin
from .models import Extension, ExtensionTranslation
from DjangoProjectStsnDev import settings


class ExtensionAdminForm(forms.ModelForm):
    class Meta:
        model = Extension
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Создаем поля для всех языков и всех переводимых полей
        for lang_code, lang_name in settings.LANGUAGES:
            for field in ExtensionTranslation.get_translatable_fields():
                self.add_translation_field(lang_code, lang_name, field)

    def add_translation_field(self, lang_code, lang_name, field_name):
        field_key = f"{field_name}_{lang_code}"
        translation = self.get_translation(lang_code)
        initial_value = getattr(translation, field_name, '') if translation else ''

        self.fields[field_key] = forms.CharField(
            label=f"{ExtensionTranslation._meta.get_field(field_name).verbose_name} ({lang_name})",
            initial=initial_value,
            required=False,
            widget=forms.Textarea if field_name == 'description' else forms.TextInput
        )

    def get_translation(self, lang_code):
        if self.instance.pk:
            try:
                return self.instance.translations.get(language_code=lang_code)
            except ExtensionTranslation.DoesNotExist:
                return None
        return None

    def save(self, commit=True):
        instance = super().save(commit=commit)
        self.save_translations(instance)
        return instance

    def save_translations(self, instance):
        for lang_code, _ in settings.LANGUAGES:
            trans_data = {}
            for field in ExtensionTranslation.get_translatable_fields():
                field_key = f"{field}_{lang_code}"
                trans_data[field] = self.cleaned_data.get(field_key, '')

            ExtensionTranslation.objects.update_or_create(
                extension=instance,
                language_code=lang_code,
                defaults=trans_data
            )


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

    def get_fields(self, request, obj=None):
        # Возвращаем только оригинальные поля модели Extension
        return ['name', 'version', 'file', 'secret_key', 'trial_period_days']

    def get_fieldsets(self, request, obj=None):
        # Основные поля
        fieldsets = [
            (None, {
                'fields': self.get_fields(request, obj)
            }),
        ]

        # Добавляем секции для переводов
        for lang_code, lang_name in settings.LANGUAGES:
            fieldsets.append(
                (f"{lang_name} Translation", {
                    'fields': [
                        f"name_{lang_code}",
                        f"title_{lang_code}",
                        f"short_description_{lang_code}",
                        f"description_{lang_code}",
                        f"meta_description_{lang_code}"
                    ],
                    'classes': ('collapse',)
                })
            )

        return fieldsets

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('translations')

