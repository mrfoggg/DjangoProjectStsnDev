from django.db import models
from django.utils.translation import gettext_lazy as _

class Extension(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('extension_name'))
    file_id = models.PositiveIntegerField(null=True, blank=True)
    secret_key = models.CharField(max_length=255, verbose_name=_('secret_key'))

    class Meta:
        verbose_name = _('extension')
        verbose_name_plural = _('extensions')

    def __str__(self):
        return self.name