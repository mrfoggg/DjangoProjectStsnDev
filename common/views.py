from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import LoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/custom_login.html'
    # form_class = LoginForm
    # success_url = reverse_lazy('home')  # Замените 'home' на ваш URL-паттерн

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Передаем объект request в форму
        return kwargs