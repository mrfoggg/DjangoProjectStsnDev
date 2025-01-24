from django.contrib import admin
from .models import Customer, Developer, Extension, ForumFile, Order, OrderFile


class OrderFileInline(admin.TabularInline):  # Можно заменить на StackedInline для другого отображения
    model = OrderFile
    extra = 1  # Количество пустых строк для добавления новых записей


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Order._meta.get_fields()]
    list_display = ['id', 'date', 'customer', 'total_amount', 'status']

    inlines = [OrderFileInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email']


@admin.register(ForumFile)
class ForumFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'developer']
    readonly_fields = ['extension_name']


@admin.register(Extension)
class ExtensionAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_id']


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email']
    readonly_fields = ['credits']
