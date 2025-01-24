from rest_framework import serializers
from .models import ForumCustomer, Developer, ForumFile, Order, OrderFile

class OrderSerializer(serializers.ModelSerializer):
    developer_id = serializers.IntegerField(write_only=True)
    developer_name = serializers.CharField(write_only=True)
    developer_email = serializers.EmailField(write_only=True)
    developer_link = serializers.CharField(write_only=True)
    developer_credits = serializers.HStoreField(write_only=True)

    customer_id = serializers.IntegerField(write_only=True)
    customer_name = serializers.CharField(write_only=True)
    customer_email = serializers.EmailField(write_only=True)
    customer_link = serializers.CharField(write_only=True)

    file_id = serializers.IntegerField(write_only=True)
    file_name = serializers.CharField(write_only=True)
    file_link = serializers.CharField(write_only=True)

    domain = serializers.CharField(write_only=True)
    test_domain = serializers.CharField(write_only=True)

    class Meta:
        model = Order
        exclude = ['customer']

    def save(self, **kwargs):
        validated_data = self.validated_data

        developer_id = validated_data.pop('developer_id', None)
        developer_name = validated_data.pop('developer_name', '')
        developer_email = validated_data.pop('developer_email', '')
        developer_link = validated_data.pop('developer_link', '')
        developer_credits = validated_data.pop('developer_credits', {})

        customer_id = validated_data.pop('customer_id', None)
        customer_name = validated_data.pop('customer_name', '')
        customer_email = validated_data.pop('customer_email', '')
        customer_link = validated_data.pop('customer_link', '')

        file_id = validated_data.pop('file_id', None)
        file_name = validated_data.pop('file_name', '')
        file_link = validated_data.pop('file_link', '')

        domain = validated_data.pop('domain', '')
        test_domain = validated_data.pop('test_domain', '')

        # Создание или обновление разработчика
        developer, _ = Developer.objects.update_or_create(
            id=developer_id,
            defaults={
                'name': developer_name,
                'email': developer_email,
                'link': developer_link,
                'credits': developer_credits,
            }
        )

        # Создание или обновление клиента
        customer, _ = ForumCustomer.objects.update_or_create(
            id=customer_id,
            defaults={
                'name': customer_name,
                'email': customer_email,
                'link': customer_link,
            }
        )

        # Создание или обновление файла
        file, _ = ForumFile.objects.get_or_create(
            id=file_id,
            defaults={
                'name': file_name,
                'link': file_link,
                'developer': developer,
            }
        )

        # Создание или обновление заказа
        order_id = validated_data.pop('id', None)

        # Убедитесь, что customer_id передается корректно
        validated_data['customer_id'] = customer.id

        order, created = Order.objects.update_or_create(
            id=order_id,
            defaults=validated_data
        )

        # Создание или обновление связи заказа с файлом
        OrderFile.objects.get_or_create(
            file=file,
            domain=domain,
            order=order,
            defaults={
                'test_domain': test_domain,
            }
        )

        return order
