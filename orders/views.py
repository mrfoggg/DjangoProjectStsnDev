from rich import print
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
import hmac
import hashlib

class OrderWebhook(APIView):
    private_key = "11112222333442"

    def post(self, request):
        data = request.data

        if not data:
            print("Received empty data.")
            return self.create_response({'detail': 'Invalid request format'}, status.HTTP_400_BAD_REQUEST)

        print('WEBHOOOOOK POST', data)

        # Проверка подписи
        hash_value = data.get('hash')
        if 'order' not in data or not hash_value:
            return self.create_response({'detail': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)

        order_id = str(data['order']['id'])
        order_date = str(data['order']['date'])

        expected_hash = hmac.new(
            self.private_key.encode(),
            (str(len(order_id)) + order_id + str(len(order_date)) + order_date).encode(),
            hashlib.md5
        ).hexdigest()

        if hash_value != expected_hash:
            return self.create_response({'detail': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)

        # Обработка по статусу
        status_code = data.get('status')
        if status_code == 'auth':
            return self.create_response({'state': 'Authorized', 'detail': 'Ready to receive form'}, status.HTTP_200_OK)

        elif status_code == 'success':
            # Сериализация данных происходит только при статусе `success`
            serializer = OrderSerializer(data={
                'order_id': data['order']['id'],
                'date': data['order']['date'],
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
                return self.create_response({'state': 'Received', 'detail': 'Form successfully received'}, status.HTTP_200_OK)
            else:
                return self.create_response({'state': 'Error', 'errors': serializer.errors}, status.HTTP_400_BAD_REQUEST)

        return self.create_response({'detail': 'Unknown status'}, status.HTTP_400_BAD_REQUEST)

    def create_response(self, data, http_status):
        """Создание ответа с добавлением заголовка `State`."""
        response = Response(data, status=http_status)
        response['State'] = 'Received' if http_status == status.HTTP_200_OK else 'Error'
        return response
