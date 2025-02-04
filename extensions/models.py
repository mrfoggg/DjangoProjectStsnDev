from django.db import models
from django.utils.translation import gettext_lazy as _
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

    @property
    def current_lang_translation(self):
        return self.translations.filter(language_code=get_language()).first()


class ExtensionTranslation(models.Model):
    extension = models.ForeignKey('Extension', related_name='translations', on_delete=models.CASCADE)
    language_code = models.CharField(max_length=15, db_index=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField()
    short_description = models.TextField()
    title = models.CharField(max_length=255)
    meta_description = models.TextField()

    class Meta:
        unique_together = ('extension', 'language_code')

    @classmethod
    def get_translatable_fields(cls):
        # Возвращает все поля типа CharField и TextField, исключая поле 'language_code'
        return [
            field for field in cls._meta.fields
            if isinstance(field, (models.fields.CharField, models.fields.TextField)) and field.name != 'language_code'
        ]

class ExtensionProxy(Extension):
    class Meta:
        proxy = True

    def get_translation(self, language_code):

        return self.translations.filter(language_code=language_code).first()

    def set_translation(self, language_code, field, value):
        translation = self.get_translation(language_code)
        if translation:
            setattr(translation, field, value)
            translation.save()
        else:
            translation = self.translations.create(language_code=language_code)
            setattr(translation, field, value)
            translation.save()

    @property
    def description_current_language(self):
        current_language = get_language()
        translation = self.get_translation(current_language)
        return translation.description if translation else None

    # Возвращает объект перевода: ExtensionTranslation, который соответствует текущему языку.
    @property
    def current_lang_fields_translation(self):
        return self.get_translation(get_language())
