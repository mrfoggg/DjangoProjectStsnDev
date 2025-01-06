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
        try:
            data = request.data

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
                return self.create_response({'detail': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)

            # Обработка по статусу
            status_value = data.get('status')
            if status_value == 'auth':
                return self.create_response({'state': 'Received'}, status.HTTP_200_OK)

            elif status_value == 'success':
                # Проверяем наличие всех данных
                order_data = data.get('order', {})
                customer_data = data.get('customer', {})
                developer_data = data.get('developer', {})

                # Сохранение заказа
                serializer = OrderSerializer(data={
                    'order_id': order_data.get('id'),
                    'date': order_data.get('date'),
                    'domain': order_data.get('domain'),
                    'test_domain': order_data.get('test_domain'),
                    'total_amount': order_data.get('total', {}).get('amount'),
                    'currency': order_data.get('total', {}).get('currency'),
                    'customer_name': customer_data.get('name'),
                    'customer_email': customer_data.get('email'),
                    'developer_name': developer_data.get('name'),
                    'developer_email': developer_data.get('email'),
                })

                if serializer.is_valid():
                    serializer.save()
                    return self.create_response({'state': 'Received'}, status.HTTP_200_OK)
                else:
                    return self.create_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

            else:
                return self.create_response({'detail': 'Unsupported status'}, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Логирование ошибки и возврат ответа
            print(f"Error: {e}")
            return self.create_response({'detail': 'Internal server error'}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_response(self, data, http_status):
        """Создание ответа с добавлением заголовка `State`."""
        response = Response(data, status=http_status)
        response['State'] = 'Received' if http_status == status.HTTP_200_OK else 'Error'
        return response
