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
            return Response({'State': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        request_type = data.get('status', '')
        print('STATUS', request_type)
        if request_type == "auth":
            print('===AUTH===')
            return Response({'State': 'Authorized'}, status=status.HTTP_200_OK)

        elif request_type == "success":
            print('===success===')
            return Response({'state': 'Received'}, status=status.HTTP_200_OK)


