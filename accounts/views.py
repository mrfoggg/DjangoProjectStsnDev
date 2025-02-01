from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone  # Импорт timezone
import uuid  # Импорт uuid
from .models import EmailVerification, CustomUser  # Импорт моделей
from .forms import EmailRegistrationForm, LoginForm


class CustomLoginView(LoginView):
    template_name = 'registration/custom_login.html'
    form_class = LoginForm


def registration_email_verification(request):
    if request.method == 'POST':
        form = EmailRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Проверка, если email уже есть в базе пользователей CustomUser
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Этот email уже используется. Пожалуйста, войдите в аккаунт.')
                return redirect('register')  # Возвращаем на страницу регистрации

            # Проверка, если email уже есть в таблице EmailVerification
            verification, created = EmailVerification.objects.get_or_create(email=email)
            if not created:
                # Если запись уже существует, обновляем token и created_at
                verification.token = uuid.uuid4()
                verification.created_at = timezone.now()
                verification.save()

            # Генерация ссылки для активации
            activation_url = request.build_absolute_uri(
                reverse('activate_account', kwargs={'token': verification.token}))

            # Отправка письма с подтверждением
            try:
                send_mail(
                    'Подтверждение email',
                    f'Для активации аккаунта перейдите по следующей ссылке: {activation_url}',
                    'admin@yourdomain.com',
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, 'Произошла ошибка при отправке письма. Пожалуйста, попробуйте снова.')
                return redirect('register')  # Возвращаем на страницу регистрации

            return redirect('email_verification_sent')
    else:
        form = EmailRegistrationForm()

    return render(request, 'registration/email_registration.html', {'form': form})
