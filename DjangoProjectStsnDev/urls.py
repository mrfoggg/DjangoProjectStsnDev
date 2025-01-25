from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('orders/', include('orders.urls')),
    path('', include('home.urls')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)
