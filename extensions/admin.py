from django.contrib import admin
from django import forms
from .models import Extension, ExtensionTranslation, ExtensionProxy
from unfold.admin import ModelAdmin, TabularInline


class ExtensionTranslationInline(admin.TabularInline):
    model = ExtensionTranslation
    extra = 1
    fields = ('language_code', 'name', 'description', 'short_description', 'title', 'meta_description')


class ExtensionProxyForm(forms.ModelForm):
    """Форма для отображения виртуальных полей в админке"""

    name_en = forms.CharField(label="Название (EN)", required=False)
    name_ru = forms.CharField(label="Название (RU)", required=False)
    description_en = forms.CharField(label="Описание (EN)", widget=forms.Textarea, required=False)
    description_ru = forms.CharField(label="Описание (RU)", widget=forms.Textarea, required=False)

    class Meta:
        model = ExtensionProxy
        fields = ['name', 'version', 'secret_key', 'trial_period_days', 'name_en', 'name_ru', 'description_en', 'description_ru']

    def __init__(self, *args, **kwargs):
        """Заполняем поля перевода текущими значениями"""
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['name_en'].initial = self.instance.get_translation('en').name if self.instance.get_translation('en') else ''
            self.fields['name_ru'].initial = self.instance.get_translation('ru').name if self.instance.get_translation('ru') else ''
            self.fields['description_en'].initial = self.instance.get_translation('en').description if self.instance.get_translation('en') else ''
            self.fields['description_ru'].initial = self.instance.get_translation('ru').description if self.instance.get_translation('ru') else ''

    def save(self, commit=True):
        """Сохраняем переводные поля"""
        instance = super().save(commit=False)
        instance.set_translation('en', 'name', self.cleaned_data['name_en'])
        instance.set_translation('ru', 'name', self.cleaned_data['name_ru'])
        instance.set_translation('en', 'description', self.cleaned_data['description_en'])
        instance.set_translation('ru', 'description', self.cleaned_data['description_ru'])
        if commit:
            instance.save()
        return instance


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    list_display = ('name', 'version', 'secret_key', 'trial_period_days')
    inlines = [ExtensionTranslationInline]
    search_fields = ('name', 'version', 'secret_key')


@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm  # Указываем кастомную форму
    list_display = ('name', 'name_en', 'name_ru', 'description_en', 'description_ru')
    fieldsets = (
        ('Основная информация', {'fields': ('name', 'version', 'secret_key', 'trial_period_days')}),
        ('Переводы', {'fields': ('name_en', 'name_ru', 'description_en', 'description_ru')}),
    )

    @admin.display(description="Название (EN)")
    def name_en(self, obj):
        return obj.get_translation('en').name if obj.get_translation('en') else "-"

    @admin.display(description="Название (RU)")
    def name_ru(self, obj):
        return obj.get_translation('ru').name if obj.get_translation('ru') else "-"

    @admin.display(description="Описание (EN)")
    def description_en(self, obj):
        return obj.get_translation('en').description if obj.get_translation('en') else "-"

    @admin.display(description="Описание (RU)")
    def description_ru(self, obj):
        return obj.get_translation('ru').description if obj.get_translation('ru') else "-"
