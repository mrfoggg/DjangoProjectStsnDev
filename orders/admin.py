from django.contrib import admin
from .models import Developer, ForumFile, Order, Customer


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Order._meta.get_fields()]
    list_display = ['id', 'date', 'customer', 'total_amount']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email']


@admin.register(ForumFile)
class ForumFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'developer']


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email']
    readonly_fields = ['credits']
