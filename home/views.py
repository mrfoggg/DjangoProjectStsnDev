from django.db.models import OuterRef, Subquery, F
from django.db.models.functions import JSONObject
from django.utils.translation import get_language
from django.shortcuts import render
from django.utils.translation import gettext as _

from extensions.models import Extension, ExtensionTranslation
from rich import print


def index(request):
    current_language = get_language()

    # Подзапрос для получения перевода
    translation_subquery = ExtensionTranslation.objects.filter(
        extension=OuterRef('pk'),
        language_code=current_language
    ).annotate(
        translation_json=JSONObject(
            name=F('name'),
            title=F('title'),
            short_description=F('short_description'),
            slug=F('slug'),
        )
    ).values('translation_json')[:1]

    # Основной запрос
    extensions = Extension.objects.annotate(
        translation=Subquery(translation_subquery)
    ).values('version', 'trial_period_days', 'translation')

    context = {
        'install_info': _("all_install_text"),
        'extensions': extensions
    }
    print('SESSION - ', request.session.items())
    return render(request, 'index.html', context)
