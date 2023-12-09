from django.urls import path
from .views import HelloWorldView, RegistrationView, login_view, logout_view,  ClientRegistrationView, ClientDeleteView, search_clients, RegistrationRequestView
from .views import ListClientsView, AddFieldToClientView, InitiateActionView, CloseActionView, ActionListView, RegistrationRequestList, RegistrationRequestDetail
from .views import ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='api_logout'),
    path('api/register-client/', ClientRegistrationView.as_view(), name='register-client'),
    path('api/delete-client/<int:pk>/', ClientDeleteView.as_view(), name='delete-client'),
    path('api/search-clients/', search_clients, name='search-clients'),
    path('api/list-clients/', ListClientsView.as_view(), name='list-clients'),
    path('api/add-field-to-client/<int:client_id>/', AddFieldToClientView.as_view(), name='add-field-to-client'),
    path('api/initiate-action/<int:client_id>/', InitiateActionView.as_view(), name='initiate-action'),
    path('api/close-action/<int:action_id>/', CloseActionView.as_view(), name='close-action'),
    path('api/list-actions/', ActionListView.as_view(), name='list-actions'),
    path('api/user-registration-request/', RegistrationRequestView.as_view(), name='user_registration_request'),
    path('registration-requests/', RegistrationRequestList.as_view(), name='registration-request-list'),
    path('registration-requests/<int:pk>/', RegistrationRequestDetail.as_view(), name='registration-request-detail'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]
