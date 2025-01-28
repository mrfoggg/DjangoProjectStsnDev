from django.contrib import admin
from .models import ForumCustomer, Developer, ForumFile, Order, OrderFile
from django.contrib.admin import TabularInline  # Используем стандартный TabularInline

class OrderFileInline(TabularInline):  # Можно заменить на StackedInline для другого отображения
    model = OrderFile
    extra = 1  # Количество пустых строк для добавления новых записей
    tab = True

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['id', 'date', 'customer', 'total_amount', 'status']
    fields = [('id', 'customer'), 'date', ('currency', 'total_amount', 'commission'), 'status']

    inlines = [OrderFileInline]

@admin.register(ForumCustomer)
class CustomerAdmin(admin.ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['id', 'name', 'email']

@admin.register(ForumFile)
class ForumFileAdmin(admin.ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['id', 'name', 'developer']
    readonly_fields = ['extension_name']

@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['id', 'name', 'email']
    readonly_fields = ['credits']
