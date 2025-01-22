from django.contrib.postgres.fields import HStoreField
from django.db import models

class Order(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    date = models.DateTimeField()

    currency = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    commission = models.DecimalField(max_digits=15, decimal_places=2)

    domain = models.CharField(max_length=255)
    test_domain = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.total_amount}"


class Developer(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    link = models.URLField(max_length=200, verbose_name="Ссылка на профиль")
    credits = HStoreField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.name}"


class Customer(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    link = models.URLField(max_length=200, verbose_name="Ссылка на пользователя")

    def __str__(self):
        return f"Order {self.id} - {self.name}"


class ForumFile(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=200, verbose_name="Ссылка на расщирение")

    def __str__(self):
        return f"Order {self.id} - {self.name}"

