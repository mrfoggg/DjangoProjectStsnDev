from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

import hashlib
from urllib.parse import urlparse


class ForumCustomer(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_("nickname"))
    email = models.EmailField(verbose_name=_("email"))
    link = models.URLField(max_length=200, verbose_name=_("user_link"))

    class Meta:
        verbose_name = _("forum_user")
        verbose_name_plural = _("forum_users")

    def __str__(self):
        return f"{self.id} - {self.name}"


class Developer(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, verbose_name=_("nickname"))
    email = models.EmailField(verbose_name=_("email"))
    link = models.URLField(max_length=200, verbose_name=_("user_link"))
    credits = HStoreField(null=True, blank=True, verbose_name=_("credits"))

    class Meta:
        verbose_name = _("developer_account")
        verbose_name_plural = _("developer_accounts")


    def __str__(self):
        return f"{self.id} - {self.name}"


class Extension(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    file_id = models.PositiveIntegerField(null=True, blank=True)
    secret_key = models.CharField(max_length=255, verbose_name='Секретный ключ')

    class Meta:
        verbose_name = 'Расширение'
        verbose_name_plural = 'Расширения'

    def __str__(self):
        return self.name


class ForumFile(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Название')
    link = models.URLField(max_length=200, verbose_name="Расширение на форуме")
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name="files")

    class Meta:
        verbose_name = 'Файл на форуме'
        verbose_name_plural = 'Файлы на форуме'

    def __str__(self):
        return f"{self.id} - {self.name} ({self.developer.name})"

    @property
    def extension(self):
        return Extension.objects.filter(file_id=self.id).first()

    def extension_name(self):
        if self.extension:
            admin_edit_url = reverse('admin:orders_extension_change', args=[self.extension.pk])
            return format_html('<a href="{}">{}</a>', admin_edit_url, self.extension.name)
        return 'Нет соответствия'

    extension_name.short_description = 'Расширение'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('processed', 'Обработан'),
        ('email_sent', 'Письмо отправлено'),
        ('email_failed', 'Ошибка отправки письма'),
    ]

    id = models.PositiveIntegerField(unique=True, primary_key=True)
    date = models.DateTimeField(verbose_name='Дата покупки')
    currency = models.CharField(max_length=10, verbose_name='Валюта')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Итого')
    commission = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Комиссия')
    customer = models.ForeignKey(ForumCustomer, on_delete=models.CASCADE, verbose_name='Покупатель')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"


class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name = 'Заказ')
    file = models.ForeignKey(ForumFile, on_delete=models.CASCADE, verbose_name = 'Файл на форуме')

    domain = models.CharField(max_length=255, verbose_name='Домен')
    test_domain = models.CharField(max_length=255, blank=True, null=True, verbose_name='Тестовый домен')

    domain_license = models.CharField(max_length=255, blank=True, null=True, verbose_name='Лицензионный ключ')
    test_domain_license = models.CharField(max_length=255, blank=True, null=True, verbose_name='Лицензионный ключ для тестового домена')

    class Meta:
        unique_together = ('order', 'file', 'domain')
        verbose_name = 'Файл в заказе'
        verbose_name_plural = 'Файлы в заказе'

    def __str__(self):
        return f"Order {self.order.id} - {self.file.name}"

    def save(self, *args, **kwargs):
        extension = self.file.extension
        if extension:
            # Обработка домена
            parsed_domain = urlparse(self.domain)
            clean_domain = parsed_domain.hostname  # Извлекаем только доменное имя

            # Генерация domain_license
            domain_license_hash = hashlib.sha256(f"{extension.secret_key}{clean_domain}".encode()).hexdigest()
            self.domain_license = domain_license_hash

            # Генерация test_domain_license, если test_domain задан
            if hasattr(self, 'test_domain') and self.test_domain:
                parsed_test_domain = urlparse(self.test_domain)
                clean_test_domain = parsed_test_domain.hostname  # Извлекаем только доменное имя
                test_domain_license_hash = hashlib.sha256(f"{extension.secret_key}{clean_test_domain}".encode()).hexdigest()
                self.test_domain_license = test_domain_license_hash

        super().save(*args, **kwargs)
