from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registration_email_verification, CustomLoginView

urlpatterns = [
    path('register/', registration_email_verification, name='register'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/client_logged_out.html'),
         name='logout'),
    path('login/', CustomLoginView.as_view(template_name='registration/custom_login.html'),
         name='client_login'),
]
