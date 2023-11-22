# backend/urls.py
from django.urls import path
from .views import register_admin, register_client, AdminLoginView, ClientLoginView

urlpatterns = [
    # Add a home page URL if needed
    path('', home, name='home'),

    # Registration URLs
    path('register/admin/', register_admin, name='register_admin'),
    path('register/client/', register_client, name='register_client'),

    # Login URLs
    path('login/admin/', AdminLoginView.as_view(), name='login_admin'),
    path('login/client/', ClientLoginView.as_view(), name='login_client'),

    # Add other URLs as needed
]
