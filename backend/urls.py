# backend/urls.py
from django.urls import path
from .views import register_admin, register_client

urlpatterns = [
    # Other patterns
    path('register/admin/', register_admin, name='register_admin'),
    path('register/client/', register_client, name='register_client'),
    path('login/admin/', AdminLoginView.as_view(), name='login_admin'),
    path('login/client/', ClientLoginView.as_view(), name='login_client'),
]
