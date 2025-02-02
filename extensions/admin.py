from django.contrib import admin
from django.template.context import Context

from DjangoProjectStsnDev import settings
from extensions.models import Extension, ExtensionTranslation
from unfold.admin import ModelAdmin

# @admin.register(Extension)
# class ExtensionAdmin(ModelAdmin):  # Заменяем на стандартный ModelAdmin
#     list_display = ['name', 'file_id']
#     fields = [('name', 'version'), ('file_id', 'secret_key'), ('file', 'trial_period_days')]

from django.contrib import admin
from .models import Extension, ExtensionTranslation
from .forms import ExtensionAdminForm
from rich import print

class ExtensionAdmin(admin.ModelAdmin):
    form = ExtensionAdminForm

    def get_fieldsets(self, request, obj=None):
        """
        Переопределение get_fieldsets для добавления динамических полей переводов.
        """
        fieldsets = super().get_fieldsets(request, obj) or []
        dynamic_fields = []

        if obj:  # Только если это не новая запись
            translations = ExtensionTranslation.objects.filter(extension=obj)
            for lang_code, lang_name in settings.LANGUAGES:
                # Если перевода нет — создаем пустую запись
                if lang_code not in {t.language_code for t in translations}:
                    ExtensionTranslation.objects.create(extension=obj, language_code=lang_code)

                dynamic_fields += [
                    f'name_{lang_code}',
                    f'description_{lang_code}',
                    f'short_description_{lang_code}',
                    f'title_{lang_code}',
                    f'meta_description_{lang_code}',
                ]

        # Возвращаем поле переводов динамически
        return fieldsets + [(None, {'fields': dynamic_fields})]


    # def get_form(self, request, obj=None, **kwargs):
    #     """
    #     Переопределяем get_form для использования нашей кастомной формы.
    #     """
    #     # print('DEBUG filelds - ', self.get_fields(request))
    #     form = super().get_form(request, obj, **kwargs)
    #
    #     return form

    def save_model(self, request, obj, form, change):
        """
        Сначала сохраняем основной объект, затем обрабатываем переводы.
        """
        super().save_model(request, obj, form, change)

        from DjangoProjectStsnDev import settings  # Подгружаем список языков
        for lang_code, _ in settings.LANGUAGES:
            translation, created = ExtensionTranslation.objects.get_or_create(
                extension=obj, language_code=lang_code
            )

            # Обновляем переводы из формы
            for field in ['name', 'description', 'short_description', 'title', 'meta_description']:
                form_field = f"{field}_{lang_code}"
                if form_field in form.cleaned_data:
                    setattr(translation, field, form.cleaned_data[form_field])

            translation.save()


admin.site.register(Extension, ExtensionAdmin)

class ExtensionTranslationAdmin(ModelAdmin):
    """
    Отображает все поля модели ExtensionTranslation в админке.
    """
    list_display = [field.name for field in ExtensionTranslation._meta.fields]  # Вывод всех полей
    list_filter = ('language_code',)
    search_fields = ('name', 'title', 'extension__name')

admin.site.register(ExtensionTranslation, ExtensionTranslationAdmin)
