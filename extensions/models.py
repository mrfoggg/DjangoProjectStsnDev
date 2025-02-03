from functools import partial

from django.db import models
from django.utils.translation import gettext_lazy as _
from DjangoProjectStsnDev import settings


class Extension(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('extension_name'))
    version = models.CharField(max_length=50, blank=True, null=True, default='')
    file_id = models.PositiveIntegerField(null=True, blank=True)
    secret_key = models.CharField(max_length=255, verbose_name=_('secret_key'))
    file = models.FileField(upload_to='mod_files/', blank=True, null=True)
    trial_period_days = models.PositiveSmallIntegerField(default=30)

    class Meta:
        verbose_name = _('extension')
        verbose_name_plural = _('extensions')

    def __str__(self):
        return self.name

class ExtensionTranslation(models.Model):
    LANGUAGE_CHOICES = [(code, name) for code, name in settings.LANGUAGES]
    extension = models.ForeignKey(
        Extension,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_('extension')
    )
    language_code = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        verbose_name=_('language_code')
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Языковый перевод'
        verbose_name_plural = 'Языковые переводы'

    def __str__(self):
        return self.name

    @classmethod
    def get_translatable_fields(cls):
        return ['name', 'title', 'short_description', 'description', 'meta_description']



class ExtensionProxy(Extension):
    class Meta:
        proxy = True  # Указываем, что модель будет прокси и не создаст новую таблицу

    # Список языков и атрибутов модели
    languages = ['en', 'ru', 'fr']
    attributes = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Создаем динамические свойства для каждого языка и каждого атрибута
        for lang in self.languages:
            for attr in self.attributes:
                # Создаем и добавляем геттер и сеттер для каждого языка и атрибута
                def getter(self, lang=lang, attr=attr):
                    translation = self.get_translation(lang)
                    if translation:
                        return getattr(translation, attr, None)
                    return None

                def setter(self, value, lang=lang, attr=attr):
                    translation = self.get_translation(lang)
                    if translation:
                        setattr(translation, attr, value)
                        translation.save()
                    else:
                        # Создаем новый перевод, если его нет
                        translation = self.translations.create(language_code=lang, **{attr: value})
                        translation.save()

                # Добавляем свойства в класс для каждого языка и атрибута
                setattr(self.__class__, f'{attr}_{lang}', property(lambda self, lang=lang, attr=attr: getter(self, lang, attr), lambda self, value, lang=lang, attr=attr: setter(self, value, lang, attr)))

    def get_translation(self, language_code):
        """Возвращает перевод для заданного языка, если он существует."""
        return self.translations.filter(language_code=language_code).first()





