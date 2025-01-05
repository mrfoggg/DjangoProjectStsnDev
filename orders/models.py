from django.db import models

class Order(models.Model):
    order_id = models.IntegerField(unique=True)
    date = models.DateTimeField()
    domain = models.CharField(max_length=255)
    test_domain = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.FloatField()
    currency = models.CharField(max_length=10)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    developer_name = models.CharField(max_length=255)
    developer_email = models.EmailField()

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
