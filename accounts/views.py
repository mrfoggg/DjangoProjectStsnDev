from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
import uuid
import redis

from .forms import EmailRegistrationForm, CustomLoginForm, SetPasswordFormWithConfirmation
from .models import CustomUser

from .forms import CustomSetPasswordForm


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

            return redirect('email_verification_sent_success')
    else:
        form = EmailRegistrationForm()

    return render(request, 'email_registration.html', {'form': form})

def email_verification_sent_success(request):
    return render(request, 'email_verification_sent_success.html')


def activate_account(request, token):
    # Пытаемся получить email из Redis по токену
    email = redis_client.get(f"email_verification_token:{token}")

    if email:
        # Пытаемся найти пользователя по email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        if user:
            # Проверяем, активирован ли пользователь
            if user.is_active:
                # Если активирован и пароль установлен, перенаправляем в личный кабинет
                if user.password:
                    messages.success(request, 'Ваш аккаунт уже активирован и пароль установлен.')
                    return redirect('dashboard')  # Перенаправление в личный кабинет
                else:
                    # Если пароль еще не установлен, перенаправляем на форму установки пароля
                    messages.info(request, 'Вы успешно подтвердили почту, но еще не установили пароль.')
                    return redirect('set_password')  # Перенаправление на форму установки пароля
            else:
                # Если активация еще не произошла, активируем аккаунт
                user.is_active = True
                user.save()
                # Удаляем токен из Redis после активации
                redis_client.delete(f"email_verification_token:{token}")
                messages.success(request, 'Ваш аккаунт успешно активирован!')
                return redirect('set_password')  # Перенаправляем на форму установки пароля
        else:
            # Если пользователя нет в базе, создаем нового
            user = CustomUser.objects.create(email=email, is_active=True)
            user.save()
            # Удаляем токен из Redis после создания аккаунта
            redis_client.delete(f"email_verification_token:{token}")
            messages.success(request, 'Аккаунт создан и активирован! Пожалуйста, установите пароль.')
            return redirect('set_password')  # Перенаправляем на форму установки пароля
    else:
        messages.error(request, 'Ссылка для активации недействительна.')

    return redirect('register')


def set_password_view(request):
    # Проверяем, что пользователь ещё не установил пароль
    if request.user.is_authenticated and not request.user.has_usable_password():
        if request.method == 'POST':
            form = SetPasswordFormWithConfirmation(data=request.POST)
            if form.is_valid():
                # Сохраняем новый пароль
                password = form.cleaned_data["new_password"]
                request.user.set_password(password)
                request.user.save()
                messages.success(request, 'Пароль успешно установлен!')
                return redirect('login')  # Перенаправляем на страницу входа
        else:
            form = SetPasswordFormWithConfirmation()

        return render(request, 'custom_set_password.html', {'form': form})

    # Если пользователь уже установил пароль
    messages.info(request, 'Вы уже установили пароль. Перейдите в личный кабинет.')
    return redirect('profile')  # Перенаправляем на страницу профиля или кабинетеренаправляем на страницу профиля или кабинет
