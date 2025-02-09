from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import get_language
from django.views.generic.detail import DetailView
from .models import ExtensionTranslation
from rich import print

class ExtensionTranslationDetailView(DetailView):
    model = ExtensionTranslation
    context_object_name = 'extension'
    template_name = 'extension_detail.html'

    def get_object(self, queryset=None):
        language_code = get_language()

        return get_object_or_404(
            ExtensionTranslation,
            slug=self.kwargs['slug'],
            language_code=language_code
        )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущий объект Extension
        extension = self.object.extension

        # Используем values_list для получения кортежей (код языка, slug)
        language_slug_list = extension.translations.values_list('language_code', 'slug')

        # Преобразуем QuerySet в словарь для удобства использования в шаблоне
        language_slug_dict = dict(language_slug_list)

        # Добавляем словарь в контекст
        context['language_slug_dict'] = language_slug_dict

        return context

