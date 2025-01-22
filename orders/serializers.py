from rest_framework import serializers
from .models import Order, Developer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        # Извлекаем данные, которые нужно сохранить в связанных таблицах
        # customer_name = validated_data.pop('customer_name')
        # customer_email = validated_data.pop('customer_email')
        developer_id = validated_data.pop('developer_id')
        developer_name = validated_data.pop('developer_name')
        developer_email = validated_data.pop('developer_email')
        developer_link = validated_data.pop('developer_link')
        developer_credits = validated_data.pop('developer_credits')

        # Сохраняем данные в таблицу Customer
        # customer, _ = Customer.objects.get_or_create(
        #     email=customer_email,
        #     defaults={'name': customer_name}
        # )

        # Сохраняем данные в таблицу Developer
        developer, _ = Developer.objects.get_or_create(
            id=developer_id,
            defaults={'name': developer_name, 'email': developer_email, 'link': developer_link, 'credits': developer_credits}
        )

        # Сохраняем данные в основную таблицу Order, связывая её с Customer и Developer
        order = Order.objects.create(
            **validated_data,
            # customer_name=customer.name,  # Пример, если нужно сохранить в Order имя заказчика
            # developer_name=developer.name  # Пример, если нужно сохранить имя разработчика
        )

        return order
