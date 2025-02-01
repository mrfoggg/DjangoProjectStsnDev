from django.contrib.auth.views import LoginView
from .forms import EmailRegistrationForm, CustomLoginForm
import uuid
import redis
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from .forms import EmailRegistrationForm
from .models import CustomUser

class CustomLoginView(LoginView):
    template_name = 'custom_login.html'
    form_class = CustomLoginForm


# Подключаемся к Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def registration_get_email(request):
    if request.method == 'POST':
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Проверяем, есть ли email в базе пользователей
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Этот email уже используется. Пожалуйста, войдите в аккаунт.')
                return redirect('register')

            # Генерируем токен
            token = str(uuid.uuid4())

            # Сохраняем токен в Redis с TTL (например, 10 минут)
            redis_client.setex(f"email_verification:{email}", 600, token)

            # Генерируем ссылку для активации
            activation_url = request.build_absolute_uri(
                reverse('activate_account', kwargs={'token': token})
            )

            # Отправляем письмо
            try:
                send_mail(
                    'Подтверждение email',
                    f'Для активации аккаунта перейдите по следующей ссылке: {activation_url}',
                    'admin@yourdomain.com',
                    [email],
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, 'Ошибка при отправке письма. Попробуйте снова.')
                return redirect('register')

            return redirect('email_verification_sent')
    else:
        form = EmailRegistrationForm()

    return render(request, 'email_registration.html', {'form': form})

