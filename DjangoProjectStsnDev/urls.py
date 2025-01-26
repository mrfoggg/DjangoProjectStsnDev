from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.i18n import set_language
from .views import CustomLoginView  # Импортируйте кастомное представление логина

urlpatterns = [
    path('orders/', include('orders.urls')),
    path('', include('home.urls')),
]

# Локализация
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('set_language/', set_language, name='set_language'),
    prefix_default_language=False,
)

# Маршруты для аутентификации и кастомное представление логина
urlpatterns += [
    # path('accounts/', include('django.contrib.auth.urls')),  # Стандартные маршруты аутентификации
    path('accounts/login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),  # Ваш кастомный путь для логина
    path('client/logout/', auth_views.LogoutView.as_view(template_name='registration/client_logged_out.html'), name='client_logout'),
]
