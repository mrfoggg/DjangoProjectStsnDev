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
        proxy = True  # Прокси-модель, не создающая новую таблицу

    def get_translation(self, language_code):
        """Кешируем переводы, чтобы не делать лишние запросы"""
        if not hasattr(self, '_translation_cache'):
            self._translation_cache = {t.language_code: t for t in self.translations.all()}
        return self._translation_cache.get(language_code)

    # Динамические свойства для переведенных полей
    def _get_translation_property(field):
        def getter(self, lang):
            translation = self.get_translation(lang)
            return getattr(translation, field, None) if translation else None

        def setter(self, lang, value):
            self.set_translation(lang, field, value)

        return property(lambda self, lang=field.split('_')[-1]: getter(self, lang),
                        lambda self, value, lang=field.split('_')[-1]: setter(self, lang, value))

    for field in ExtensionTranslation.get_translatable_fields():
        for lang_code, _ in settings.LANGUAGES:
            prop_name = f"{field}_{lang_code}"
            locals()[prop_name] = _get_translation_property(field)

    def set_translation(self, language_code, field, value):
        """Устанавливает перевод для указанного поля и языка."""
        translation = self.get_translation(language_code)
        if translation:
            setattr(translation, field, value)
        else:
            translation = self.translations.create(extension=self, language_code=language_code, **{field: value})
        translation.save()



