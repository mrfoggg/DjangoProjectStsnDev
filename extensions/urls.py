from django.urls import path
from .views import ExtensionTranslationDetailView

urlpatterns = [
    path('<slug:slug>/', ExtensionTranslationDetailView.as_view(), name='extension_detail'),
]
