# login_views.py
from django.contrib.auth.views import LoginView
from .forms import LoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
