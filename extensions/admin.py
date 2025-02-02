from django.contrib import admin
from .models import Extension, ExtensionTranslation, ExtensionProxy

class ExtensionTranslationInline(admin.TabularInline):
    model = ExtensionTranslation
    extra = 1
    fields = ('language_code', 'name', 'description', 'short_description', 'title', 'meta_description')

class ExtensionAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'secret_key', 'trial_period_days')
    inlines = [ExtensionTranslationInline]
    search_fields = ('name', 'version', 'secret_key')

class ExtensionProxyAdmin(ExtensionAdmin):
    list_display = (
        'name_all_languages',
        'description_all_languages',
        'short_description_all_languages',
        'title_all_languages',
        'meta_description_all_languages',
    )
    search_fields = ('name', 'description', 'short_description', 'title', 'meta_description')

    def name_all_languages(self, obj):
        return f"EN: {obj.name_en} | RU: {obj.name_ru}"
    name_all_languages.short_description = 'Name'

    def description_all_languages(self, obj):
        return f"EN: {obj.description_en} | RU: {obj.description_ru}"
    description_all_languages.short_description = 'Description'

    def short_description_all_languages(self, obj):
        return f"EN: {obj.short_description_en} | RU: {obj.short_description_ru}"
    short_description_all_languages.short_description = 'Short Description'

    def title_all_languages(self, obj):
        return f"EN: {obj.title_en} | RU: {obj.title_ru}"
    title_all_languages.short_description = 'Title'

    def meta_description_all_languages(self, obj):
        return f"EN: {obj.meta_description_en} | RU: {obj.meta_description_ru}"
    meta_description_all_languages.short_description = 'Meta Description'

admin.site.register(Extension, ExtensionAdmin)
admin.site.register(ExtensionProxy, ExtensionProxyAdmin)
