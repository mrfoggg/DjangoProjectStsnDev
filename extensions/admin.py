from django.contrib import admin
from django.template.context import Context
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
    """
    Кастомный ModelAdmin для Extension с редактированием языковых полей.
    """
    form = ExtensionAdminForm
    # fields = [field.name for field in ExtensionTranslation._meta.fields]
    list_display = ('name', 'version', 'secret_key')
    # print('DEBUG filelds - ', )

    def get_fields(self, request, obj=None):
        """
        Переопределение get_fields для добавления динамических полей переводов.
        """
        fields = super().get_fields(request, obj)

        if obj:  # Только если это не новая запись
            # Получаем переводы для данного объекта
            translations = ExtensionTranslation.objects.filter(extension=obj)
            existing_langs = {t.language_code for t in translations}

            from DjangoProjectStsnDev import settings  # Получаем список доступных языков
            dynamic_fields = []

            for lang_code, lang_name in settings.LANGUAGES:
                # Если перевода нет — создаем пустую запись
                if lang_code not in existing_langs:
                    ExtensionTranslation.objects.create(extension=obj, language_code=lang_code)

                # Добавляем динамические поля переводов
                dynamic_fields += [
                    f'name_{lang_code}',
                    f'description_{lang_code}',
                    f'short_description_{lang_code}',
                    f'title_{lang_code}',
                    f'meta_description_{lang_code}'
                ]

            # Добавляем поля переводов к основным полям модели
            fields += dynamic_fields

        return fields

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
