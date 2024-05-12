from django.contrib import admin, auth
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.http import JsonResponse
from django.contrib import messages
from .views.custom_user_views import RegistrationView, UserDeactivateView, UserActivateView
from .models import CustomUser, UserActionLog, Client, Service, PasswordResetToken, Event, Alert, Reservation, Reports

class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_time', 'action_type', 'permission', 'granted_by', 'granted_by_fullname')
    search_fields = ('user__email', 'action_type', 'granted_by__email', 'granted_by_fullname')

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'FirstName', 'is_staff', 'isActive', 'get_groups')
    list_filter = ('is_staff', 'groups', 'isActive')  # Adjusted list_filter
    actions = ['deactivate_users', 'activate_users']

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

    def deactivate_users(self, request, queryset):
        for user in queryset:
            print(f"Deactivating user {user.UserID}")
            try:
                view = UserDeactivateView.as_view()
                request_data = {'pk': user.UserID}  # Adjust this based on your API's expected data
                response = view(request, **request_data)
                print(f"Response from deactivate view is: {response}")
                if response.status_code == 200:
                    self.message_user(request, f"User '{user}' deactivated successfully.", messages.SUCCESS)
                else:
                    self.message_user(request, f"Failed to deactivate user '{user}'. Error: {response.data.get('message')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Failed to deactivate user '{user}'. Error: {str(e)}", messages.ERROR)

    def activate_users(self, request, queryset):
        for user in queryset:
            print(f"Activating user {user.UserID}")
            try:
                view = UserActivateView.as_view()
                request_data = {'pk': user.UserID}  # Adjust this based on your API's expected data
                response = view(request, **request_data)
                print(f"Response from activate view is: {response}")    
                if response.status_code == 200:
                    self.message_user(request, f"User '{user}' activated successfully.", messages.SUCCESS)
                else:
                    self.message_user(request, f"Failed to activate user '{user}'. Error: {response.data.get('message')}", messages.ERROR)
            except Exception as e:
                self.message_user(request, f"Failed to activate user '{user}'. Error: {str(e)}", messages.ERROR)

# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('register_users/', self.admin_view(RegistrationView.as_view()), name='register_users'),
        ]
        return custom_urls + urls

admin_site = CustomAdminSite(name='custom_admin')
admin.site = admin_site

# Register your models with the custom admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserActionLog, UserActionLogAdmin)
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(PasswordResetToken)
admin.site.register(Event)
admin.site.register(Alert)
admin.site.register(Reservation)
admin.site.register(Reports)

admin.site.site_header = 'ML Corporate Services Admin'
admin.site.site_title = 'ML Corporate Services'

