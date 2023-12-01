from django.urls import path
from .views import HelloWorldView, RegistrationView, login_view, logout_view,  ClientRegistrationView

urlpatterns = [
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='api_logout'),
    path('api/register-client/', ClientRegistrationView.as_view(), name='register-client'),
]
