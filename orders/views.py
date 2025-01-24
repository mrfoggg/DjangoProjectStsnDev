from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rich import print
from .models import Order, OrderFile
from .serializers import OrderSerializer
from .tasks import process_order
import hmac
import hashlib
from django.core.mail import send_mail
from django.conf import settings

class OrderWebhook(APIView):
    private_key = "11112222333442"

    def post(self, request):
        data = request.data
        print('DATA', data)

        # Проверка подписи
        hash_value = data.get('hash')
        order_id = str(data['order']['id'])
        order_date = str(data['order']['date'])
        expected_hash = hmac.new(
            self.private_key.encode(),
            (str(len(order_id)) + order_id + str(len(order_date)) + order_date).encode(),
            hashlib.md5
        ).hexdigest()

        if hash_value != expected_hash:
            return Response(status=status.HTTP_401_UNAUTHORIZED, headers={'State': 'Unauthorized'})

        request_type = data.get('status', '')
        if request_type == "auth":
            return Response(status=status.HTTP_200_OK, headers={'State': 'Authorized'})

        elif request_type == "success":
            order_timestamp = int(data['order']['date'])  # Получаем timestamp
            order_date_obj = datetime.fromtimestamp(order_timestamp)  # Преобразуем в datetime объект
            formatted_order_date = order_date_obj.isoformat()  # Получаем строку в формате ISO 8601

            order_data = {
                'id': data['order']['id'],
                'date': formatted_order_date,
                'domain': data['order']['domain'],
                'test_domain': data['order']['test_domain'],
                'currency': data['order']['total']['currency'],
                'total_amount': data['order']['total']['amount'],
                'commission': data['order']['commission'],
                'developer_id': data['developer']['id'],
                'developer_name': data['developer']['name'],
                'developer_email': data['developer']['email'],
                'developer_link': data['developer']['link'],
                'developer_credits': {item['currency']: str(item['amount']) for item in data['developer'].get('credits', [])},
                'customer_id': data['customer']['id'],
                'customer_name': data['customer']['name'],
                'customer_email': data['customer']['email'],
                'customer_link': data['customer']['link'],
                'file_id': data['file']['id'],
                'file_name': data['file']['name'],
                'file_link': data['file']['link'],
            }

            print('DATA - ', order_data)

            serializer = OrderSerializer(data=order_data)

            if serializer.is_valid():
                print("VALID DATA:", serializer.validated_data)
                order = serializer.save()

                # Проверяем статус заказа
                if order.status == 'new':
                    # Устанавливаем статус "processing"
                    order.status = 'processing'
                    order.save()

                    # Вызываем задачу Celery для обработки заказа
                    print(f"Sending task for order {order.id} with countdown 3 seconds")
                    process_order.apply_async((order.id,), countdown=3)
            else:
                print('serializer.errors - ', serializer.errors)
            return Response(status=status.HTTP_200_OK, headers={'State': 'Received'})
