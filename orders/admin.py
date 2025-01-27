from django.contrib import admin
from .models import ForumCustomer, Developer, Extension, ForumFile, Order, OrderFile
from unfold.admin import ModelAdmin, TabularInline


class OrderFileInline(TabularInline):  # Можно заменить на StackedInline для другого отображения
    model = OrderFile
    extra = 1  # Количество пустых строк для добавления новых записей
    tab = True


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    # list_display = [field.name for field in Order._meta.get_fields()]
    list_display = ['id', 'date', 'customer', 'total_amount', 'status']
    fields = [('id', 'customer'), 'date', ('currency', 'total_amount', 'commission'), 'status']

    inlines = [OrderFileInline]


@admin.register(ForumCustomer)
class CustomerAdmin(ModelAdmin):
    list_display = ['id', 'name', 'email']


@admin.register(ForumFile)
class ForumFileAdmin(ModelAdmin):
    list_display = ['id', 'name', 'developer']
    readonly_fields = ['extension_name']


@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):
    list_display = ['name', 'file_id']


@admin.register(Developer)
class DeveloperAdmin(ModelAdmin):
    list_display = ['id', 'name', 'email']
    readonly_fields = ['credits']
