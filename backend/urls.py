from django.urls import path
from .views import HelloWorldView, RegistrationView, login_view  # Updated import

urlpatterns = [
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/login/', login_view, name='login'),  # Updated path and view function name
]
