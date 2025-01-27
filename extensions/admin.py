from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from extensions.models import Extension


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    list_display = ['name', 'file_id']
    fields = [('name', 'version'), ('file_id', 'secret_key'), 'file', 'trial_period_days']
