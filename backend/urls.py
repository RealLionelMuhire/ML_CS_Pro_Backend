from django.urls import path
from .views import HelloWorldView, RegistrationView, login_view, logout_view,  ClientRegistrationView, ClientDeleteView, search_clients

urlpatterns = [
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='api_logout'),
    path('api/register-client/', ClientRegistrationView.as_view(), name='register-client'),
    path('api/delete-client/<int:pk>/', ClientDeleteView.as_view(), name='delete-client'),
    path('api/search-clients/', search_clients, name='search-clients'),
]
