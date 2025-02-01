from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registration_email_verification, CustomLoginView

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='custom_login.html'), name='client_login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='client_logged_out.html'), name='logout'),
    path('register/', registration_email_verification, name='register'),

]
