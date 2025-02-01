from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, send_email_verification_view, email_verification_sent_success_view, cabinet_view

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='custom_login.html'), name='client_login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='client_logged_out.html'), name='logout'),
    path('register/', send_email_verification_view, name='send_email_verification_for_register'),
    path('email_verification_sent_success/', email_verification_sent_success_view, name='email_verification_sent_success'),
    path('cabinet/', cabinet_view, name='cabinet'),

]
