from django.contrib import admin
from django.template.context import Context
from extensions.models import Extension
from unfold.admin import ModelAdmin

# @admin.register(Extension)
# class ExtensionAdmin(ModelAdmin):  # Заменяем на стандартный ModelAdmin
#     list_display = ['name', 'file_id']
#     fields = [('name', 'version'), ('file_id', 'secret_key'), ('file', 'trial_period_days')]

from django.contrib import admin
from .models import Extension, ExtensionTranslation
from .forms import ExtensionAdminForm

class ExtensionAdmin(admin.ModelAdmin):
    """
    Кастомный ModelAdmin для Extension с редактированием языковых полей.
    """
    form = ExtensionAdminForm
    list_display = ('name', 'version', 'secret_key')

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

