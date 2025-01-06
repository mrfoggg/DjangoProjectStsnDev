# serializers.py
from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'order_id', 'date', 'domain', 'test_domain',
            'total_amount', 'currency',
            'customer_name', 'customer_email',
            'developer_name', 'developer_email'
        ]
