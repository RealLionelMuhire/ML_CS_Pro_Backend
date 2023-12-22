from django.urls import path
from .views.custom_user_views import HelloWorldView, RegistrationView, get_dashboard_data, UserListView
from .views.client_views import ListClientsView, AddFieldToClientView, ListClientsView, AddFieldToClientView, search_clients, ClientRegistrationView, ClientDeactivateView, ClientActivateView
from .views.action_views import InitiateActionView, CloseActionView, ActionListView
from .views.authentication_views import login_view, logout_view,ForgotPasswordView, ResetPasswordView
from .views.permission_views import UserPermissionsView, AllPermissionsView,ActivateUserView, DeactivateUserView, GrantPermissionsView

urlpatterns = [
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='api_logout'),
    path('api/register-client/', ClientRegistrationView.as_view(), name='register-client'),
    path('api/deactivate-client/<int:pk>/', ClientDeactivateView.as_view(), name='deactivate-client'),
    path('api/activate-client/<int:pk>/', ClientActivateView.as_view(), name='activate-client'),
    path('api/search-clients/', search_clients, name='search-clients'),
    path('api/list-clients/', ListClientsView.as_view(), name='list-clients'),
    path('api/add-field-to-client/<int:client_id>/', AddFieldToClientView.as_view(), name='add-field-to-client'),
    path('api/initiate-action/<int:client_id>/', InitiateActionView.as_view(), name='initiate-action'),
    path('api/close-action/<int:action_id>/', CloseActionView.as_view(), name='close-action'),
    path('api/list-actions/', ActionListView.as_view(), name='list-actions'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('api/user-permissions/', UserPermissionsView.as_view(), name='user_permissions'),
    path('api/all-permissions/', AllPermissionsView.as_view(), name='all_permissions'),
    path('api/activate-user/<int:user_id>/', ActivateUserView.as_view(), name='activate_user'),
    path('api/deactivate-user/<int:user_id>/', DeactivateUserView.as_view(), name='deactivate_user'),
    path('api/grant-permissions/<int:user_id>/', GrantPermissionsView.as_view(), name='grant_permissions'),
    path('api/dashboard-data/', get_dashboard_data, name='get_dashboard_data')
]
