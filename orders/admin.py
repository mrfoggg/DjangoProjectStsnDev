from django.contrib import admin
from django.contrib.postgres.fields import HStoreField
from django_json_widget.widgets import JSONEditorWidget
from .models import Developer, Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.get_fields()]


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    readonly_fields = ['credits']

    # formfield_overrides = {
    #     HStoreField: {'widget': JSONEditorWidget},
    # }
