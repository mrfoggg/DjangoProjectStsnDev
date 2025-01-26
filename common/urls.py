from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='registration/client_logged_out.html'),
         name='client_logout'),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='client_login'),
    # path('accounts/login/', CustomLoginView.as_view(template_name='registration/login.html'), name='client_login'),
    path('accounts/', include('django.contrib.auth.urls')),  # Стандартные маршруты аутентификации
]
