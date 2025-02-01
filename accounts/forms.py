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


class SetPasswordFormWithConfirmation(forms.Form):
    new_password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
        required=True,
        min_length=8,
        help_text="Пароль должен содержать не менее 8 символов."
    )
    confirm_password = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}),
        required=True,
        help_text="Введите тот же пароль еще раз."
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data

