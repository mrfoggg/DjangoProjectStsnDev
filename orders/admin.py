from django.contrib import admin
from .models import Developer, ForumFile, Order, Customer


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.get_fields()]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']


@admin.register(ForumFile)
class ForumFileAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
    readonly_fields = ['credits']
