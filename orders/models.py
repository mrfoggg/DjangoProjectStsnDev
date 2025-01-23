from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.urls import reverse
from django.utils.html import format_html


class Customer(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    link = models.URLField(max_length=200, verbose_name="Ссылка на пользователя")

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
        return f"{self.id} - {self.name}"

    @property
    def extension(self):
        return Extension.objects.filter(file_id=self.id).first()

    def extension_name(self):
        if self.extension:
            admin_edit_url = reverse('admin:orders_forumfile_change', args=[self.pk])
            return format_html('<a href="{}">{}</a>', admin_edit_url, self.extension.name)
        return 'Нет соответствия'

    extension_name.short_description = 'Расширение'



class Order(models.Model):
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    date = models.DateTimeField()

    currency = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=2)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"


class OrderFile(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.ForeignKey(ForumFile, on_delete=models.CASCADE)

    domain = models.CharField(max_length=255)
    test_domain = models.CharField(max_length=255, blank=True, null=True)

    domain_license = models.CharField(max_length=255, blank=True, null=True)
    test_domain_license = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order {self.order.id} - {self.file.name}"







