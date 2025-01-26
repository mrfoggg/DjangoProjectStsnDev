from django.contrib.auth.views import LoginView
from .forms import LoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/custom_login.html'
    form_class = LoginForm
