from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [

    path('logout/', auth_views.LogoutView.as_view(template_name='registration/client_logged_out.html'),
         name='client_logout'),
    path('login/', CustomLoginView.as_view(), name='client_login'),
    path('accounts/', include('django.contrib.auth.urls')),  # Стандартные маршруты аутентификации
]
