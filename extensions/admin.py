from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ExtensionProxy
from .forms import ExtensionProxyForm

@admin.register(ExtensionProxy)
class ExtensionProxyAdmin(ModelAdmin):
    form = ExtensionProxyForm
    list_display = ('name', 'description_current_language')
    fieldsets = (
        ("Основная информация", {
            'fields': ('name', 'version', 'secret_key', 'trial_period_days'),
        }),
        ("Название", {
            'fields': ('name_en', 'name_ru', 'name_uk'),
        }),
        ("Заголовок", {
            'fields': ('title_en', 'title_ru', 'title_uk'),
        }),
        ("Краткое описание", {
            'fields': ('short_description_en', 'short_description_ru', 'short_description_uk'),
        }),
        ("Полное описание", {
            'fields': ('description_en', 'description_ru', 'description_uk'),
        }),
        ("Поисковое описание", {
            'fields': ('meta_description_en', 'meta_description_ru', 'meta_description_uk'),
        }),
    )
