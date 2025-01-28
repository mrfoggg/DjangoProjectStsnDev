from django.contrib import admin
from django.template.context import Context
from extensions.models import Extension
from unfold.admin import ModelAdmin

@admin.register(Extension)
class ExtensionAdmin(ModelAdmin):  # Заменяем на стандартный ModelAdmin
    list_display = ['name', 'file_id']
    fields = [('name', 'version'), ('file_id', 'secret_key'), ('file', 'trial_period_days')]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('context_data____', context)  # Выводим весь контекст в консоль
        return context
