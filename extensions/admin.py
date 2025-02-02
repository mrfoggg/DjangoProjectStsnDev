from django.contrib import admin
from .models import Extension, ExtensionTranslation, ExtensionProxy
from unfold.admin import ModelAdmin, TabularInline


class ExtensionTranslationInline(admin.TabularInline):
    model = ExtensionTranslation
    extra = 1
    fields = ('language_code', 'name', 'description', 'short_description', 'title', 'meta_description')


class ExtensionAdmin(ModelAdmin):
    list_display = ('name', 'version', 'secret_key', 'trial_period_days')
    inlines = [ExtensionTranslationInline]
    search_fields = ('name', 'version', 'secret_key')


class ExtensionProxyAdmin(ModelAdmin):
    list_display = ('name', 'get_name_en', 'get_name_ru', 'get_description_en', 'get_description_ru')

    def _get_translated_field(field):
        def getter(self, obj):
            return getattr(obj, field, "-") or "-"
        getter.short_description = field.replace("_", " ").title()
        return getter

    for field in ['name_en', 'name_ru', 'description_en', 'description_ru']:
        locals()[f'get_{field}'] = _get_translated_field(field)

admin.site.register(Extension, ExtensionAdmin)
admin.site.register(ExtensionProxy, ExtensionProxyAdmin)
