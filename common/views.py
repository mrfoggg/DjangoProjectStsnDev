from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('home')  # Замените 'home' на ваш URL-паттерн
