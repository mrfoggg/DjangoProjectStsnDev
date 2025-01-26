from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import LoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    # success_url = reverse_lazy('home')  # Замените 'home' на ваш URL-паттерн
