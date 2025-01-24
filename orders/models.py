from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
import hashlib
from urllib.parse import urlparse


class ForumCustomer(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    link = models.URLField(max_length=200, verbose_name="Ссылка на пользователя")

    class Meta:
        verbose_name = 'Пользователь форума'
        verbose_name_plural = 'Пользователи форума'

    def __str__(self):
        return f"{self.id} - {self.name}"


class Developer(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    link = models.URLField(max_length=200, verbose_name="Ссылка на профиль")
    credits = HStoreField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Extension(models.Model):
    name = models.CharField(max_length=255)
    file_id = models.PositiveIntegerField(null=True, blank=True)
    secret_key = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ForumFile(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=200, verbose_name="Расширение на форуме")
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name="files", verbose_name='Разработчик')

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
        ('new', 'New'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('email_sent', 'Email Sent'),
        ('email_failed', 'Email Failed'),
    ]

    id = models.PositiveIntegerField(unique=True, primary_key=True)
    date = models.DateTimeField()

    currency = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=2)

    customer = models.ForeignKey(ForumCustomer, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"


class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.ForeignKey(ForumFile, on_delete=models.CASCADE)

    domain = models.CharField(max_length=255)
    test_domain = models.CharField(max_length=255, blank=True, null=True)

    domain_license = models.CharField(max_length=255, blank=True, null=True)
    test_domain_license = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('order', 'file', 'domain')

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
