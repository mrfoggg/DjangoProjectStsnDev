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
    list_display = ('name', 'name_en', 'name_ru', 'description_en', 'description_ru')

    @admin.display(description="Название (EN)")
    def name_en(self, obj):
        return obj.get_name('en') or "-"

    @admin.display(description="Название (RU)")
    def name_ru(self, obj):
        return obj.get_name('ru') or "-"

    @admin.display(description="Описание (EN)")
    def description_en(self, obj):
        return obj.get_description('en') or "-"

    @admin.display(description="Описание (RU)")
    def description_ru(self, obj):
        return obj.get_description('ru') or "-"


admin.site.register(Extension, ExtensionAdmin)
admin.site.register(ExtensionProxy, ExtensionProxyAdmin)
