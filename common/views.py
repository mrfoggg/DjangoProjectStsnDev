from django.contrib.auth.views import LoginView
from .forms import LoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/custom_login.html'
    form_class = LoginForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Передаем объект request в форму
        return kwargs
