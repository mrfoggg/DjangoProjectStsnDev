from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
    path('', include('home.urls')),
]

# urlpatterns += i18n_patterns(
#     path('admin/', admin.site.urls),
#     path('set_language/', set_language, name='set_language'),
#     prefix_default_language=False,
# )

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
