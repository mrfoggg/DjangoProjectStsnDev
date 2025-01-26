from django.urls import path
from . import views

app_name = 'home' # app_name используется для пространств имен, чтобы Django мог различать маршруты с одинаковыми именами в разных приложениях.

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
]