from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderFile

@shared_task
def process_order(order_id):
    # Получаем заказ и связанные данные из базы данных
    order = Order.objects.get(id=order_id)
    order_files = OrderFile.objects.filter(order=order)

    # Устанавливаем статус "processed"
    order.status = 'processed'
    order.save()

    # Формирование сообщения
    subject = f"Заказ {order.id} успешно создан"
    message = f"""
    Уважаемый(ая) {order.customer.name},

    Ваш заказ {order.id} успешно создан.

    Расширения с форума:
    """

    for order_file in order_files:
        message += f"""
        {order_file.file.name}
        Домен: {order_file.domain}
        Лицензия: {order_file.domain_license}
        """
        if order_file.test_domain_license:
            message += f"""
        Тестовый домен: {order_file.test_domain}
        Тестовая лицензия: {order_file.test_domain_license}
        """

    # Отправка письма
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            fail_silently=False,
        )
        # Устанавливаем статус "email_sent"
        order.status = 'email_sent'
    except Exception as e:
        print(f"Failed to send email: {e}")
        # Устанавливаем статус "email_failed"
        order.status = 'email_failed'

    order.save()
