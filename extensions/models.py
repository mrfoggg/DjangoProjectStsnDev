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

    # Список языков и полей
    languages = ['en', 'ru', 'fr']
    fields = ['name', 'description']  # Пример полей

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически создаем свойства для каждого поля и языка
        for field in self.fields:
            for lang in self.languages:
                # Используем partial для создания геттеров и сеттеров
                getter = partial(self.get_translation_field, lang, field)
                setter = partial(self.set_translation_field, lang, field)

                # Добавляем свойство с геттером и сеттером
                setattr(self.__class__, f"{field}_{lang}", property(getter, setter))

    def get_translation(self, language_code):
        """Возвращает перевод для заданного языка, если он существует."""
        return self.translations.filter(language_code=language_code).first()

    def get_translation_field(self, lang, field):
        """Геттер для перевода поля."""
        translation = self.get_translation(lang)
        return getattr(translation, field) if translation else None

    def set_translation_field(self, lang, field, value):
        """Сеттер для перевода поля."""
        translation = self.get_translation(lang)
        if translation:
            setattr(translation, field, value)
            translation.save()
        else:
            translation = self.translations.create(language_code=lang, **{field: value})
            translation.save()


    # # Виртуальные поля для каждого языка
    # @property
    # def name_en(self):
    #     return self.get_translation('en').name if self.get_translation('en') else None
    #
    # @property
    # def description_en(self):
    #     return self.get_translation('en').description if self.get_translation('en') else None



    # @property
    # def name_ru(self):
    #     return self.get_translation('ru').name if self.get_translation('ru') else None
    #
    # @property
    # def description_ru(self):
    #     return self.get_translation('ru').description if self.get_translation('ru') else None



    # def get_translation(self, language_code):
    #     """Возвращает перевод для заданного языка, если он существует."""
    #     return self.translations.filter(language_code=language_code).first()
    #
    # def set_translation(self, language_code, field, value):
    #     """Добавляем метод для сохранения переводов"""
    #     translation = self.get_translation(language_code)
    #     if translation:
    #         setattr(translation, field, value)
    #         translation.save()
    #     else:
    #         # Если перевода нет, создаем новый
    #         translation = self.translations.create(language_code=language_code)
    #         setattr(translation, field, value)
    #         translation.save()


