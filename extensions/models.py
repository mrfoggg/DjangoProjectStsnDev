from django.db import models
from django.utils.translation import gettext_lazy as _
from DjangoProjectStsnDev import settings
from django.utils.translation import get_language


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
        proxy = True
        verbose_name = _('Extension with translations')
        verbose_name_plural = _('Extensions with translations')

    def __get_translation(self, language_code):
        return self.translations.filter(language_code=language_code).first()

    def __create_translation_property(field_name):
        def getter(self):
            for lang_code, _ in settings.LANGUAGES:
                if translation := self.__get_translation(lang_code):
                    return getattr(translation, field_name, '')
            return ''

        def setter(self, value):
            for lang_code, _ in settings.LANGUAGES:
                translation = self.__get_translation(lang_code) or ExtensionTranslation(
                    extension=self,
                    language_code=lang_code
                )
                setattr(translation, field_name, value)
                translation.save()

        return property(getter, setter)

    # Динамическое создание свойств для всех полей переводов
    for field in ['name', 'title', 'short_description', 'description', 'meta_description']:
        for lang_code, lang_name in settings.LANGUAGES:
            locals()[f'{field}_{lang_code}'] = __create_translation_property(field)
