from rest_framework import serializers
from .models import Order, Developer

class OrderSerializer(serializers.ModelSerializer):
    developer_id = serializers.IntegerField(write_only=True)
    developer_name = serializers.CharField(write_only=True)
    developer_email = serializers.EmailField(write_only=True)
    developer_link = serializers.CharField(write_only=True)
    developer_credits = serializers.HStoreField(write_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        print('DDATA', validated_data)
        developer_credits = validated_data.pop('developer_credits', {})
        print("CREDITS IN CREATE:", developer_credits)
        print("CREDITS TYPE IN CREATE:", type(developer_credits))

        # Сохранение Developer
        developer_id = validated_data.pop('developer_id', None)
        developer_name = validated_data.pop('developer_name', '')
        developer_email = validated_data.pop('developer_email', '')
        developer_link = validated_data.pop('developer_link', '')

        if developer_id:
            obj, created = Developer.objects.update_or_create(
                id=developer_id,
                defaults={
                    'name': developer_name,
                    'email': developer_email,
                    'link': developer_link,
                    'credits': '',
                }
            )

        # Сохранение Order
        order = Order.objects.create(**validated_data)
        return order

