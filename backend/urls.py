from django.urls import path
from .views import HelloWorldView, RegistrationView, LoginView

urlpatterns = [
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/login/', LoginView.as_view(), name='login'),
]
