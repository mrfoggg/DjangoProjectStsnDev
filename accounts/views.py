from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

import uuid
import redis

from .forms import EmailVerificationForm, CustomLoginForm, SetPasswordFormWithConfirmation
from .models import CustomUser


class CustomLoginView(LoginView):
    template_name = 'custom_login.html'
    form_class = CustomLoginForm

# Подключаемся к Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


def send_email_verification_view(request):
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            token = str(uuid.uuid4())
            redis_client.setex(f"email_verification:{email}", 600, token)

            # Генерация ссылки для активации
            activation_url = request.build_absolute_uri(
                reverse('activate_account', kwargs={'email': email, 'token': token})
            )

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

            return redirect('email_verification_sent_success')
    else:
        form = EmailVerificationForm()

    return render(request, 'email_registration.html', {'form': form})

def email_verification_sent_success_view(request):
    return render(request, 'email_verification_sent_success.html')

def cabinet_view(request):
    return render(request, 'cabinet.html')


def activate_account_view(request, email=None, token=None):
    try:
        user = CustomUser.objects.get(email=email)
        login(request, user)
        print(f"DEBUG: user.password = {repr(user.password)}")
        print(f"DEBUG: has_usable_password() = {user.has_usable_password()}")
        if user.password and user.has_usable_password():
            messages.info(request, 'Ваш аккаунт уже активирован и пароль установлен.')
            return redirect('cabinet')  # Личный кабин
        else:
            messages.info(request, 'Ваш аккаунт активен, но вы еще не установили пароль.')
            return redirect('set_password')  # Перенаправляем на форму установки пароля

    except CustomUser.DoesNotExist:
        stored_token = redis_client.get(f"email_verification:{email}")

        if stored_token is None:
            messages.error(request, 'Ссылка для активации недействительна или срок ее действия истек.')
            return redirect('send_email_verification_for_register')

        if stored_token == token:
            # Создаем пользователя
            user = CustomUser.objects.create(email=email)
            user.save()
            login(request, user)

            # Удаляем токен из Redis
            redis_client.delete(f"email_verification:{email}")

            # Перенаправляем на страницу установки пароля
            messages.info(request, 'Вы успешно подтвердили почту, но еще не установили пароль.')
            return redirect('set_password')

        else:
            messages.error(request, 'Ссылка для активации недействительна.')
            return redirect('register')


def set_password_view(request):
    # Проверяем, что пользователь ещё не установил пароль
    if request.user.is_authenticated and not request.user.has_usable_password():
        if request.method == 'POST':
            form = SetPasswordFormWithConfirmation(user=request.user, data=request.POST)
            if form.is_valid():
                # Сохраняем новый пароль
                password = form.cleaned_data["new_password"]
                request.user.set_password(password)
                request.user.save()
                messages.success(request, 'Пароль успешно установлен!')
                return redirect('cabinet')  # Перенаправляем на страницу входа
        else:
            form = SetPasswordFormWithConfirmation(user=request.user)

        return render(request, 'custom_set_password.html', {'form': form})

    # Если пользователь уже установил пароль
    messages.info(request, 'Вы уже установили пароль. Перейдите в личный кабинет.')
    return redirect('cabinet')  # Перенаправляем на страницу профиля или кабинет

