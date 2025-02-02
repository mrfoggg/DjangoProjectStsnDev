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

class ExtensionProxyAdmin(ExtensionAdmin):
    list_display = ('name', 'name_en', 'name_ru', 'description_en', 'description_ru')
    search_fields = ('name', 'name_en', 'name_ru', 'description_en', 'description_ru')

admin.site.register(Extension, ExtensionAdmin)
admin.site.register(ExtensionProxy, ExtensionProxyAdmin)
