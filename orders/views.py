from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
import hmac
import hashlib

class OrderWebhook(APIView):
    private_key = "ваш_секретный_ключ"

    def post(self, request):
        data = request.data

        # Проверка подписи
        hash_value = data.get('hash')
        order_id = str(data['order']['id'])
        order_date = str(data['order']['date'])
        expected_hash = hmac.new(
            self.private_key.encode(),
            (len(order_id) + order_id + len(order_date) + order_date).encode(),
            hashlib.md5
        ).hexdigest()

        if hash_value != expected_hash:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Сохранение заказа
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
            return Response({'state': 'Received'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
