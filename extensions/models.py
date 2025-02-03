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
        unique_together = ('extension', 'language_code')
        verbose_name = _('translation')
        verbose_name_plural = _('translations')

    def __str__(self):
        return f"{self.extension.name} ({self.language_code})"

class ExtensionProxy(Extension):
    class Meta:
        proxy = True
        verbose_name = _('Extension with translations')
        verbose_name_plural = _('Extensions with translations')

    def get_translation(self, language_code):
        return self.translations.filter(language_code=language_code).first()

    def set_translation(self, language_code, data):
        translation, created = self.translations.get_or_create(language_code=language_code)
        for field, value in data.items():
            setattr(translation, field, value)
        translation.save()
