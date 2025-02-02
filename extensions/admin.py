from django.contrib import admin
from .models import Extension, ExtensionProxy


class ExtensionProxyAdmin(admin.ModelAdmin):
    list_display = (
        'name_all_languages',
        'description_all_languages',
        'short_description_all_languages',
        'title_all_languages',
        'meta_description_all_languages',
    )

    search_fields = ('name', 'description', 'short_description', 'title', 'meta_description')

    fieldsets = (
        ('Name', {
            'fields': ('name_en', 'name_ru'),
            'legend': 'Name in all languages',
        }),
        ('Description', {
            'fields': ('description_en', 'description_ru'),
            'legend': 'Description in all languages',
        }),
        ('Short Description', {
            'fields': ('short_description_en', 'short_description_ru'),
            'legend': 'Short Description in all languages',
        }),
        ('Title', {
            'fields': ('title_en', 'title_ru'),
            'legend': 'Title in all languages',
        }),
        ('Meta Description', {
            'fields': ('meta_description_en', 'meta_description_ru'),
            'legend': 'Meta Description in all languages',
        }),
    )

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


admin.site.register(ExtensionProxy, ExtensionProxyAdmin)
