from rest_framework import serializers
from .models import Order, Developer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        Developer.objects.update_or_create(
            id=validated_data.pop('developer_id', None),
            defaults={
                'name': validated_data.pop('developer_name', ''),
                'email': validated_data.pop('developer_email', ''),
                'link': validated_data.pop('developer_link', ''),
                'credits': validated_data.pop('developer_credits', {}),
            }
        )

        # Сохранение Order
        order = Order.objects.create(**validated_data)
        return order

