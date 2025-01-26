from django import forms

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Username_',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        label='Password_',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.get('request')  # Получаем объект request, если он передан
        super().__init__(*args, **kwargs)
        # Теперь можно использовать request, если нужно