from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username__', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'}))
    password = forms.CharField(label='Password___', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
