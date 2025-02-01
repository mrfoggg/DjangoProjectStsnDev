from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm


class EmailRegistrationForm(forms.Form):
    email = forms.EmailField(
        label="Email", max_length=254, required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите ваш email',
        })
    )


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        max_length=150, label='Почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите адрес'
        })
    )
    password = forms.CharField(
        label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))

class SetPasswordFormWithConfirmation(SetPasswordForm):
    new_password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        required=True,
        min_length=8,
        help_text="Пароль должен содержать не менее 8 символов."
    )
    confirm_password = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput,
        required=True,
        help_text="Введите тот же пароль еще раз."
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data
