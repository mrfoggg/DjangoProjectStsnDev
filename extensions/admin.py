from django.contrib import admin
from django.contrib.admin import TabularInline  # Используем стандартный TabularInline
from extensions.models import Extension

@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['name', 'file_id']
    fields = [('name', 'version'), ('file_id', 'secret_key'), ('file', 'trial_period_days')]
