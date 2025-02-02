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
    name = models.CharField(max_length=255, verbose_name=_('extension_name'))
    description = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=255, verbose_name=_('extension_name'))
    title = models.CharField(max_length=255, verbose_name=_('extension_name'))
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Языковый перевод'
        verbose_name_plural = 'Языковые переводы'

    def __str__(self):
        return self.name