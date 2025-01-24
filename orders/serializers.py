from rest_framework import serializers
from .models import Customer, Developer, ForumFile, Order, OrderFile

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
        print('CREATE METHOD STARTED')
        print('VALIDATED DATA:', validated_data)
        developer_id = validated_data.pop('developer_id', None)
        developer_name = validated_data.pop('developer_name', '')
        developer_email = validated_data.pop('developer_email', '')
        developer_link = validated_data.pop('developer_link', '')
        developer_credits = validated_data.pop('developer_credits', {})

        customer_id = validated_data['customer_id']
        customer_name = validated_data.pop('customer_name', '')
        customer_email = validated_data.pop('customer_email', '')
        customer_link = validated_data.pop('customer_link', '')

        file_id = validated_data.pop('file_id', None)
        file_name = validated_data.pop('file_name', '')
        file_link = validated_data.pop('file_link', '')

        domain = validated_data.pop('domain', '')
        test_domain = validated_data.pop('test_domain', '')


        developer, _ = Developer.objects.update_or_create(
            id=developer_id,
            defaults={
                'name': developer_name,
                'email': developer_email,
                'link': developer_link,
                'credits': developer_credits,
            }
        )

        validated_data['customer'], _ = Customer.objects.update_or_create(
            id=customer_id,
            defaults={
                'name': customer_name,
                'email': customer_email,
                'link': customer_link,
            }
        )

        print('FILE ID - ', file_id)
        print('FILE NAME - ', file_name)
        print('----------------------------------------')

        file, _ = ForumFile.objects.update_or_create(
            id=file_id,
            defaults={
                'name': file_name,
                'link': file_link,
                'developer': developer,
            }
        )

        # Сохранение Order
        # order = Order.objects.create(**validated_data)

        order_id = validated_data['id']
        order, created = Order.objects.get_or_create(id=order_id, defaults=validated_data)

        # OrderFile.objects.create(order=order, file=file, domain=domain, test_domain=test_domain)
        OrderFile.objects.get_or_create(
            id=file.id,
            domain=domain,
            order=order,
        )

        return super().save(**kwargs)

