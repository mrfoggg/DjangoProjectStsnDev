from rest_framework import serializers
from .models import Order, Developer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        developer_id = validated_data.pop('developer_id', None)
        developer_email = validated_data.pop('developer_email', '')
        developer_link = validated_data.pop('developer_link', '')
        developer_credits = validated_data.pop('developer_credits', {})

        if developer_id:
            Developer.objects.update_or_create(
                id=developer_id,
                defaults={
                    'name': validated_data.pop('developer_name', ''),
                    'email': developer_email,
                    'link': developer_link,
                    'credits': developer_credits,
                }
            )

        # Сохранение Order
        order = Order.objects.create(**validated_data)
        return order

