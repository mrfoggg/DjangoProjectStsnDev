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
            return Response({'State': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        request_type = data.get('status', '')
        print('STATUS', request_type)
        if request_type == "auth":
            return Response({'State': 'Authorized'}, status=status.HTTP_200_OK)

        elif request_type == "success":
            return Response({'state': 'Received'}, status=status.HTTP_200_OK)


