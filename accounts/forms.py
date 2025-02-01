from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.urls import reverse
from django.utils.html import format_html

from accounts.models import CustomUser


class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        label="Email", max_length=254, required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите ваш email',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        # Проверка, если пользователь с таким email уже существует
        if CustomUser.objects.filter(email=email).exists():
            login_url = reverse('login')  # Ссылка на страницу входа
            error_message = format_html(
                'Аккаунт с таким email уже зарегистрирован. '
                'Пожалуйста, <a href="{}">войдите в аккаунт</a> или укажите другой email.',
                login_url
            )
            raise forms.ValidationError(error_message)

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        max_length=150, label='Почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите адрес'
        })
    )
    password = forms.CharField(
        label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем класс для полей пароля
        self.fields['new_password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Введите новый пароль'})
        self.fields['new_password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Подтвердите новый пароль'})


