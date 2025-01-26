from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),  # Стандартные маршруты аутентификации
    path('client/logout/', auth_views.LogoutView.as_view(template_name='registration/client_logged_out.html'),
         name='client_logout'),
    path('client/login/', CustomLoginView.as_view(), name='client_login'),
    # Другие URL-паттерны для общих действий
]
