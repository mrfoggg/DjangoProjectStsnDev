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

    def get_translation(self, language_code):
        """ Возвращает перевод расширения для заданного кода языка. """
        return self.translations.filter(language_code=language_code).first()

    @property
    def current_lang_translation(self):
        return self.get_translation(get_language())



class ExtensionTranslation(models.Model):
    extension = models.ForeignKey('Extension', related_name='translations', on_delete=models.CASCADE)
    language_code = models.CharField(max_length=15, db_index=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    description = models.TextField()
    meta_description = models.TextField()
    slug = models.SlugField(max_length=255, db_index=True)

    class Meta:
        unique_together = ('language_code', 'slug')

    @classmethod
    def get_translatable_fields(cls):
        # Возвращает все поля типа CharField и TextField, исключая поле 'language_code'
        return [
            field for field in cls._meta.fields
            if isinstance(field, (models.fields.CharField, models.fields.TextField)) and field.name != 'language_code'
        ]

    @classmethod
    def get_wysiwyg_widget_fields_list (cls):
        return ['description',]
