# backend/urls.py
from django.urls import path
from .views import home, register_admin, register_client, AdminLoginView, ClientLoginView, HelloWorldView, RegistrationView, LoginView

urlpatterns = [
    path('', home, name='home'),
    path('register/admin/', register_admin, name='register_admin'),
    path('register/client/', register_client, name='register_client'),
    path('login/admin/', AdminLoginView.as_view(), name='login_admin'),
    path('login/client/', ClientLoginView.as_view(), name='login_client'),
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/login/', LoginView.as_view(), name='login'),
]
