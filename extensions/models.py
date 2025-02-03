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

    languages = ['en', 'ru', 'fr']  # Список языков

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Создаем динамические свойства для каждого языка
        for lang in self.languages:
            # Создаем и добавляем геттер
            def getter(self, lang=lang):
                return self.get_translation(lang).description if self.get_translation(lang) else None

            # Создаем и добавляем сеттер
            def setter(self, value, lang=lang):
                translation = self.get_translation(lang)
                if translation:
                    translation.description = value
                    translation.save()
                else:
                    translation = self.translations.create(language_code=lang, description=value)
                    translation.save()

            # Добавляем property с геттером и сеттером
            setattr(self.__class__, f"description_{lang}", property(getter, setter))


    # # Виртуальные поля для каждого языка
    # @property
    # def name_en(self):
    #     return self.get_translation('en').name if self.get_translation('en') else None
    #
    # @property
    # def description_en(self):
    #     return self.get_translation('en').description if self.get_translation('en') else None



    @property
    def name_ru(self):
        return self.get_translation('ru').name if self.get_translation('ru') else None

    @property
    def description_ru(self):
        return self.get_translation('ru').description if self.get_translation('ru') else None



    def get_translation(self, language_code):
        """Возвращает перевод для заданного языка, если он существует."""
        return self.translations.filter(language_code=language_code).first()

    def set_translation(self, language_code, field, value):
        """Добавляем метод для сохранения переводов"""
        translation = self.get_translation(language_code)
        if translation:
            setattr(translation, field, value)
            translation.save()
        else:
            # Если перевода нет, создаем новый
            translation = self.translations.create(language_code=language_code)
            setattr(translation, field, value)
            translation.save()










#
# class ExtensionProxy(Extension):
#     class Meta:
#         proxy = True  # Указываем, что модель будет прокси и не создаст новую таблицу
#
#     # Виртуальные поля для каждого языка
#     @property
#     def translations_data(self):
#         translations = {}
#         for field in self._meta.get_fields():  # Получаем все поля модели
#             # Исключаем поля language_code и extension (основные поля для перевода)
#             if field.name not in ['language_code', 'extension', 'id']:
#                 translations[field.name] = {
#                     'en': getattr(self.get_translation('en'), field.name, None),
#                     'ru': getattr(self.get_translation('ru'), field.name, None),
#                 }
#         return translations
#
#     def get_translation(self, language_code):
#         """Возвращает перевод для заданного языка, если он существует."""
#         return self.translations.filter(language_code=language_code).first()
#
#     def set_translation(self, language_code, field, value):
#         """Добавляем метод для сохранения переводов"""
#         translation = self.get_translation(language_code)
#         if translation:
#             setattr(translation, field, value)
#             translation.save()
#         else:
#             # Если перевода нет, создаем новый
#             translation = self.translations.create(language_code=language_code)
#             setattr(translation, field, value)
#             translation.save()
#
#     def save(self):
#         # Проходим по всем полям модели и сохраняем переводы
#         for field in self._meta.get_fields():  # Все поля модели
#             if field.name not in ['language_code', 'extension', 'id']:  # Исключаем ненужные поля
#                 self.set_translation('en', field.name, getattr(self, f'{field.name}_en', ''))
#                 self.set_translation('ru', field.name, getattr(self, f'{field.name}_ru', ''))
#
#         return super().save()

