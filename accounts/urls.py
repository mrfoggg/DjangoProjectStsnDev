from django.urls import path
from django.contrib.auth import views as auth_views
from .views import send_email_verification, CustomLoginView, email_verification_sent_success, cabinet

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='custom_login.html'), name='client_login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='client_logged_out.html'), name='logout'),
    path('register/', send_email_verification, name='send_email_verification'),
    path('email_verification_sent_success/', email_verification_sent_success, name='email_verification_sent_success'),
    path('cabinet/', cabinet, name='cabinet'),

]
