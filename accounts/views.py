import uuid

import redis
from rich import print

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .forms import CustomLoginForm, CustomSetPasswordForm, EmailVerificationForm
from .models import CustomUser

def custom_csrf_failure(request, reason=""):
    messages.error(request, _("csrf_failure"))

    # Перенаправляем обратно на ту же страницу
    return redirect(request.META.get("HTTP_REFERER", "/"))


class CustomLoginView(LoginView):
    template_name = 'custom_login.html'
    form_class = CustomLoginForm

    def form_invalid(self, form):
        email = form.cleaned_data.get('username')

        # Проверяем, есть ли пользователь с таким email
        if email:
            # Проверяем существует ли пользователь
            user = authenticate(self.request, username=email, password=form.cleaned_data.get('password'))

            if user is None:
                # Неверный пароль или почта не зарегистрирована
                if not self.user_exists(email):
                    messages.error(self.request, _("email_not_registered"))
                else:
                    messages.error(self.request, _("wrong_password"))
            elif not user.password:
                # Если пароль не задан (например, аккаунт не активирован)
                messages.error(self.request, _("password_not_set"))
        else:
            messages.error(self.request, _("please_enter_valid_data"))

        return super().form_invalid(form)

    def user_exists(self, email):
        """Проверяем, существует ли пользователь с таким email"""
        return CustomUser.objects.filter(email=email).exists()

# Подключаемся к Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def send_email_verification_view(request):
    if request.method == 'POST':
        print('send_email_verification_view')
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exists():
                # Если пользователь с таким email существует
                messages.error(
                    request,
                    message=format_html(
                        _(
                            "Этот адрес электронной почты уже зарегистрирован. "
                            'Пожалуйста, <a href="{}">войдите в аккаунт</a> или укажите другой email.'
                        ),
                        reverse("client_login"),
                    )
                )
                return render(request, 'email_registration.html', {'form': form})
            token = str(uuid.uuid4())
            redis_client.setex(f"email_verification:{email}", 600, token)

            # Генерация ссылки для активации
            activation_url = request.build_absolute_uri(
                reverse('activate_account', kwargs={'email': email, 'token': token})
            )
            try:
                send_mail(
                    'Подтверждение email',
                    _("Для активации аккаунта перейдите по следующей ссылке: {}").format(activation_url),
                    'admin@yourdomain.com',
                    [email],
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, _("Ошибка при отправке письма. Попробуйте снова."))
                return redirect('register')

            return redirect('email_verification_sent_success')
        else:
            # Вывод ошибок формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _("Ошибка в поле '{}': {}").format(form[field].label, error))
    else:
        form = EmailVerificationForm()
    return render(request, 'email_registration.html', {'form': form})


def email_verification_sent_success_view(request):
    messages.info(request, _("Вам отправлено письмо со ссылкой на страницу активации аккаунта. Ссылка действительна {} минут.").format(10))
    return render(request, 'email_verification_sent_success.html')

def cabinet_view(request):
    return render(request, 'cabinet.html')


def activate_account_view(request, email=None, token=None):
    try:
        user = CustomUser.objects.get(email=email)
        login(request, user)

        if user.has_usable_password and user.password != '':
            messages.info(request, _("Ваш аккаунт уже активирован и пароль установлен."))
            return redirect('cabinet')  # Личный кабин
        else:
            messages.info(request, _("Ваш аккаунт активен, но вы еще не установили пароль."))
            return redirect('set_password')  # Перенаправляем на форму установки пароля

    except CustomUser.DoesNotExist:
        stored_token = redis_client.get(f"email_verification:{email}")

        if stored_token is None:
            messages.error(request, _("Ссылка для активации недействительна или срок ее действия истек."))
            return redirect('send_email_verification_for_register')

        if stored_token == token:
            # Создаем пользователя
            user = CustomUser.objects.create(email=email)
            user.save()
            login(request, user)

            # Удаляем токен из Redis
            redis_client.delete(f"email_verification:{email}")

            # Перенаправляем на страницу установки пароля
            messages.info(request, _("Вы успешно подтвердили почту, но еще не установили пароль."))
            return redirect('set_password')

        else:
            messages.error(request, message = _("Ссылка для активации недействительна."))
            return redirect('register')


def set_password_view(request):
    # Проверяем, что пользователь ещё не установил пароль
    if request.user is None:
        messages.error(request, _("Для получения ссылки на установку пароля введите ваш Email."))
        return redirect('register')

    if request.user.is_authenticated and request.user.password == '':
        if request.method == 'POST':
            form = CustomSetPasswordForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _("Пароль успешно установлен!"))
                return redirect('cabinet')  # Перенаправляем на страницу профиля
            else:
                # Переносим ошибки формы в сообщения
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, _("Ошибка в поле '{}': {}").format(form[field].label, error))
        else:
            form = CustomSetPasswordForm(user=request.user)

        return render(request, 'custom_set_password.html', {'form': form})

    else:
        messages.info(request, _("Пароль уже был установлен"))
    return redirect('cabinet')  # Перенаправляем на страницу профиля
