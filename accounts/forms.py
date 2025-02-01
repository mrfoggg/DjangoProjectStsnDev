from django import forms

class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email',
        })
    )

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, label='Почта', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите адрес'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))