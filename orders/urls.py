from django.urls import path
from .views import OrderWebhook

urlpatterns = [
    path('webhook/', OrderWebhook.as_view(), name='order_webhook'),
]
