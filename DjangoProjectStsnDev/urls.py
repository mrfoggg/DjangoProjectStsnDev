from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.i18n import set_language
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path('orders/', include('orders.urls')),

]

# Локализация
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('home.urls')),
    path('set_language/', set_language, name='set_language'),
    prefix_default_language=True,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
