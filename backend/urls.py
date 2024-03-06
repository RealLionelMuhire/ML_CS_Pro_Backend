# urls.py

from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from .views.custom_user_views import HelloWorldView, RegistrationView, dashboard_data_view, UserListView, UserProfileView, UserProfileUpdateView
from .views.client_views import ListClientsView, AddFieldToClientView, ListClientsView, ClientListByIdView, search_clients, ClientRegistrationView, ClientDeactivateView, ClientActivateView
from .views.services_views import InitiateServiceView, CloseServiceView, ServiceListView, ServiceListByIdView
from .views.authentication_views import login_view, logout_view,ForgotPasswordView, ResetPasswordView
from .views.permission_views import UserPermissionsView, AllPermissionsView,ActivateUserView, DeactivateUserView, GrantPermissionsView
from .views.events_view import EventDetailView, EventListView, AllEventsListView
from .views.alerts_view import AlertInitiationView, AlertListView, AlertActionView, AlertDetailView, ActiveAlertsView
from .views.customAdmin import CustomAdminLoginView
from .views.reservations_view import RegisterReservationView, ListReservedPeriodsView, ListReservationsStartingTodayView, ListPastReservationsView, ListAllReservationsView, UserRegisterReservationView, ReservationDetailView

urlpatterns = [
#admin
    path("admin/", admin.site.urls),
    path('register/', RegistrationView.as_view(), name='user-registration'),
    # path('__debug__/', include('debug_toolbar.urls')),
    path('admin/login/', CustomAdminLoginView.as_view(), name='admin_login'),
    path('api/dashboard-data/', dashboard_data_view, name='dashboard_data'),
# users
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/deactivate-user/<int:pk>/', RegistrationView.as_view(), name='deactivate_user'),
    path('api/activate-user/<int:pk>/', ActivateUserView.as_view(), name='activate_user'),
    path('api/user-profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/update-user-profile/', UserProfileUpdateView.as_view(), name='update-user-profile'),
# clients
    path('api/register-client/', ClientRegistrationView.as_view(), name='register-client'),
    path('api/deactivate-client/<int:pk>/', ClientDeactivateView.as_view(), name='deactivate-client'),
    path('api/activate-client/<int:pk>/', ClientActivateView.as_view(), name='activate-client'),
    path('api/search-clients/', search_clients, name='search-clients'),
    path('api/list-clients/', ListClientsView.as_view(), name='list-clients'),
    path('api/clients-list-by-id/', ClientListByIdView.as_view(), name='clients-list-by-id'),
    path('api/add-field-to-client/<int:client_id>/', AddFieldToClientView.as_view(), name='add-field-to-client'),
# services
    path('api/initiate-service/<int:client_id>/', InitiateServiceView.as_view(), name='initiate-service'),
    path('api/close-service/<int:service_id>/', CloseServiceView.as_view(), name='close-service'),
    path('api/list-services/', ServiceListView.as_view(), name='list-service'),
    path('api/services-list-by-id/', ServiceListByIdView.as_view(), name='services-list-by-id'),
# authentication
    path('api/logout/', logout_view, name='api_logout'),
    path('api/login/', login_view, name='login'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
# permissions
    path('api/user-permissions/', UserPermissionsView.as_view(), name='user_permissions'),
    path('api/all-permissions/', AllPermissionsView.as_view(), name='all_permissions'),
    path('api/grant-permissions/<int:user_id>/', GrantPermissionsView.as_view(), name='grant_permissions'),
# events
    path('api/events/', EventListView.as_view(), name='event-list'),
    path('api/events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('api/all-events/', AllEventsListView.as_view(), name='all-events-list'),
# alerts
    path('api/alert-initiate/<int:client_id>/', AlertInitiationView.as_view(), name='alert-initiate'),
    path('api/list-alerts/', AlertListView.as_view(), name='list-alert'),
    path('api/alert-action/<int:alert_id>/', AlertActionView.as_view(), name='alert-action'),
    path('api/alert-detail/',AlertDetailView.as_view(), name='alert-detail'),
    path('api/active-alerts/', ActiveAlertsView.as_view(), name='active-alerts'),
# reservations
    path('api/register-reservation/', RegisterReservationView.as_view(), name='register_reservation'),
    path('api/list-reserved-periods/', ListReservedPeriodsView.as_view(), name='list_reservations'),
    path('api/reservations-future/', ListReservationsStartingTodayView.as_view(), name='list_reservations_starting_today'),
    path('api/reservations-past/', ListPastReservationsView.as_view(), name='list_past_reservations'),
    path('api/list-reservations/', ListAllReservationsView.as_view(), name='list_all_reservations'),
    path('api/user-register-reservation/', UserRegisterReservationView.as_view(), name='user_register_reservation'),
    path('api/reservations/', ReservationDetailView.as_view(), name='reservation_list'),
    path('api/reservations/<int:pk>/', ReservationDetailView.as_view(), name='reservation_detail'),
    path('api/reservations/<int:pk>/update/', ReservationDetailView.as_view(), name='reservation_update'),
]

# Enable the toolbar only if DEBUG is True and the current IP is in INTERNAL_IPS.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
