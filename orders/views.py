from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rich import print
from .models import Order
from .serializers import OrderSerializer
import hmac
import hashlib

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
            print('===AUTH===')
            return Response(status=status.HTTP_200_OK, headers={'State': 'Authorized'})

        elif request_type == "success":
            print('===success===')

            # Преобразование даты в правильный формат
            try:
                # Преобразуем строку в объект datetime, предполагая формат даты, который может быть в data['order']['date']
                order_date_obj = datetime.strptime(order_date,
                                                   "%Y-%m-%dT%H:%M:%S")  # Замените формат в зависимости от вашего ввода
                formatted_order_date = order_date_obj.isoformat()  # Получаем строку в формате ISO 8601
            except ValueError:
                print(f"Неверный формат даты: {order_date}")
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Invalid date format"})

            # Создание хеша для проверки подписи

            serializer = OrderSerializer(data={
                'order_id': data['order']['id'],
                'date': formatted_order_date,
                'domain': data['order']['domain'],
                'test_domain': data['order']['test_domain'],
                'total_amount': data['order']['total']['amount'],
                'currency': data['order']['total']['currency'],
                'customer_name': data['customer']['name'],
                'customer_email': data['customer']['email'],
                'developer_name': data['developer']['name'],
                'developer_email': data['developer']['email'],
            })
            if serializer.is_valid():
                serializer.save()
            else:
                print('serializer.errors - ', serializer.errors)
            return Response(status=status.HTTP_200_OK, headers={'State': 'Received'})


