from django.contrib import admin
from extensions.models import Extension
from unfold.admin import ModelAdmin

@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['name', 'file_id']
    fields = [('name', 'version'), ('file_id', 'secret_key'), ('file', 'trial_period_days')]
