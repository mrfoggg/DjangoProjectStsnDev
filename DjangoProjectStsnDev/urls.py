from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.i18n import set_language

urlpatterns = [
    path('orders/', include('orders.urls')),
    path('', include('home.urls')),
    path('common/', include('common.urls')),
]

# Локализация
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('set_language/', set_language, name='set_language'),
    prefix_default_language=False,
)

# Маршруты для аутентификации и кастомное представление логина
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),  # Стандартные маршруты аутентификации
    path('client/logout/', auth_views.LogoutView.as_view(template_name='registration/client_logged_out.html'), name='client_logout'),
]
