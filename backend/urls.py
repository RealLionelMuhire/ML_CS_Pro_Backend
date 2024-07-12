# urls.py

from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from django.contrib import admin
from .views.custom_user_views import HelloWorldView, RegistrationView, dashboard_data_view, UserListView, UserProfileView, UserProfileUpdateView, UserProfileDetailView
from .views.client_views import ListClientsView, AddFieldToClientView, ListClientsView, ClientListByIdView, search_clients, ClientRegistrationView, ClientDeactivateView, ClientActivateView, UncompletedClientRegistrationView, UncompletedClientDisoplayView, AllIncompleteClientsView, ClientDeleteView, UncompletedClientByid, UpdateUncompletedClientView, UncompletedClientDeleteView, UpdateClientView, ClientByIdListModificationView
from .views.services_views import InitiateServiceView, CloseServiceView, ServiceListView, ServiceListByIdView
from .views.authentication_views import login_view, logout_view,ForgotPasswordView, ResetPasswordView, CustomPasswordResetDoneView
from .views.permission_views import UserPermissionsView, AllPermissionsView,ActivateUserView, DeactivateUserView, GrantPermissionsView
from .views.events_view import EventDetailView, EventListView, AllEventsListView
from .views.alerts_view import AlertInitiationView, AlertListView, AlertActionView, AlertDetailView, ActiveAlertsView
from .views.customAdmin import CustomAdminLoginView
from .views.reservations_view import RegisterReservationView, ListReservedPeriodsView, ListReservationsStartingTodayView, ListPastReservationsView, ListAllReservationsView, UserRegisterReservationView, ReservationDetailView
from .views.reports_summary_views import ReportsCreateView, ReportListView, ReportDetailView, ReportUpdateView, ReportDeleteView, ReportListByIdView
from .main_client_views.client_self_view import ClientSelfRegistrationView
from .main_client_views.client_auth import client_login_view, client_logout_view, client_ForgotPasswordView, client_ResetPasswordView



urlpatterns = [
#admin
    # path("", admin.site.urls),
    path("admin/", admin.site.urls),
    path('register/', RegistrationView.as_view(), name='user-registration'),
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/login/', CustomAdminLoginView.as_view(), name='admin_login'),
    path('api/dashboard-data/', dashboard_data_view, name='dashboard_data'),
# users
    path('api/hello/', HelloWorldView.as_view(), name='hello_world'),
    path('api/register/', RegistrationView.as_view(), name='registration'),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/deactivate-user/<int:pk>/', DeactivateUserView.as_view(), name='deactivate_user'),
    path('api/activate-user/<int:pk>/', ActivateUserView.as_view(), name='activate_user'),
    path('api/user-profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/update-user-profile/', UserProfileUpdateView.as_view(), name='update-user-profile'),
    path('api/user-self-data/', UserProfileDetailView.as_view(), name='user-data'),

# clients
    path('api/register-client/', ClientRegistrationView.as_view(), name='register-client'),
    path('api/update-client/<int:id>/', UpdateClientView.as_view(), name='update-client'),
    path('api/clients-list-by-id/<int:client_id>/', ClientByIdListModificationView.as_view(), name='client-by-id'),
    path('api/register-client/<int:client_id>/', ClientDeleteView.as_view(), name='delete-client'),
    path('api/deactivate-client/<int:pk>/', ClientDeactivateView.as_view(), name='deactivate-client'),
    path('api/activate-client/<int:pk>/', ClientActivateView.as_view(), name='activate-client'),
    path('api/search-clients/', search_clients, name='search-clients'),
    path('api/list-clients/', ListClientsView.as_view(), name='list-clients'),
    path('api/clients-list-by-id/', ClientListByIdView.as_view(), name='clients-list-by-id'),
    path('api/add-field-to-client/<int:client_id>/', AddFieldToClientView.as_view(), name='add-field-to-client'),
    path('api/incompleted-client/', UncompletedClientRegistrationView.as_view(), name='uncompleted-client'),
    path('api/update-incompleted-client/<int:id>/', UpdateUncompletedClientView.as_view(), name='update-uncompleted-client'),
    path('api/incompleted-client-data/<int:client_id>/', UncompletedClientDisoplayView.as_view(), name='uncompleted-client-data'),
    path('api/delete-incomplete-client/<int:client_id>/', UncompletedClientDeleteView.as_view(), name='delete-incomplete-client'),
    path('api/all-incomplete-clients/', AllIncompleteClientsView.as_view(), name='all-incomplete-clients'),
    path('api/incomplete-clients-list-by-id/<int:client_id>/', UncompletedClientByid.as_view(), name='uncompleted-client-list-by-id'),

# services
    path('api/initiate-service/', InitiateServiceView.as_view(), name='initiate-service'),
    path('api/close-service/<int:service_id>/', CloseServiceView.as_view(), name='close-service'),
    path('api/list-services/', ServiceListView.as_view(), name='service-list'),
    path('api/services/<int:pk>/', ServiceListByIdView.as_view(), name='service-list-by-id'),

# authentication
    path('api/logout/', logout_view, name='api_logout'),
    path('api/login/', login_view, name='login'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('api/reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('api/reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('reset_password/',
         auth_views.PasswordResetView.as_view(),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_complete'),
    # path('reset_password_complete/', CustomPasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
    #      name='password_reset_complete'),

#   reports
    path('api/create-report/', ReportsCreateView.as_view(), name='create-report'),
    path('api/list-reports/', ReportListView.as_view(), name='list-reports'),
    path('api/update-report/<int:report_id>/', ReportUpdateView.as_view(), name='update-report'),
    path('api/report-detail/<int:id>/', ReportDetailView.as_view(), name='report-detail'),
    path('api/delete-report/<int:report_id>/', ReportDeleteView.as_view(), name='delete-report'),
    path('api/reports-list-by-id/', ReportListByIdView.as_view(), name='reports-list-by-id'),

# permissions
    path('api/user-permissions/', UserPermissionsView.as_view(), name='user_permissions'),
    path('api/all-permissions/', AllPermissionsView.as_view(), name='all_permissions'),
    path('api/grant-permissions/<int:user_id>/', GrantPermissionsView.as_view(), name='grant_permissions'),
# events
    path('api/events/', EventListView.as_view(), name='event-list'),
    path('api/events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('api/all-events/', AllEventsListView.as_view(), name='all-events-list'),
# alerts
    path('api/alert-initiate/', AlertInitiationView.as_view(), name='alert-initiate'),
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

# clients self views
    path('api/client/register/', ClientSelfRegistrationView.as_view(), name='self-register-client'),

# client authentication
    path('api/client/logout/', client_logout_view, name='client_api_logout'),
    path('api/client/login/', client_login_view, name='client_login'),
    path('api/client/forgot-password/',  client_ForgotPasswordView.as_view(), name='client_forgot-password'),
    path('api/client/reset-password/<str:uidb64>/<str:token>/', client_ResetPasswordView.as_view(), name='client_reset-password'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Enable the toolbar only if DEBUG is True and the current IP is in INTERNAL_IPS.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
