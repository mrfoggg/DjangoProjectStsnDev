from django.db import models
from django.utils.translation import gettext_lazy as _
from DjangoProjectStsnDev import settings
from django.utils.translation import get_language
from django.db.models.base import ModelBase

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

# extension = Extension.objects.get(id=1)

# Получение объекта перевода для текущего языка
# translation = extension.current_lang_translation
# if translation:
#     print(translation.name)
#     print(translation.description)
#
# # Получение словаря с переводами для всех полей для текущего языка
# translations = extension.current_lang_fields_translation
# for field, value in translations.items():
#     print(f"{field}: {value}")

class ExtensionProxyMeta(ModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        translatable_fields = ExtensionTranslation.get_translatable_fields()
        language_codes = [code for code, _ in settings.LANGUAGES]

        for field in translatable_fields:
            for lang_code in language_codes:
                property_name = f"{field}_{lang_code}"

                def getter(self, field_name=field, lang=lang_code):
                    translation = self.get_translation(lang)
                    return getattr(translation, field_name) if translation else None

                setattr(new_class, property_name, property(getter))

        return new_class

class ExtensionProxy(Extension, metaclass=ExtensionProxyMeta):
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

    @property
    def current_lang_fields_translation(self):
        current_language = get_language()
        translation = self.get_translation(current_language)
        if translation:
            return {field: getattr(translation, field) for field in ExtensionTranslation.get_translatable_fields()}
        return {field: None for field in ExtensionTranslation.get_translatable_fields()}
