# backend/admin.py

from django.contrib import admin
from .models import CustomUser, UserActionLog, Client, Service, PasswordResetToken, Event, Alert
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_time', 'action_type', 'permission', 'granted_by', 'granted_by_fullname')
    search_fields = ('user__email', 'action_type', 'granted_by__email', 'granted_by_fullname')

class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'FirstName', 'is_staff','isActive', 'get_groups')
    list_filter = ('is_staff', 'groups', 'isActive')  # Adjusted list_filter

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = _('Groups')

# Register your models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserActionLog, UserActionLogAdmin)
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(PasswordResetToken)
admin.site.register(Event)
admin.site.register(Alert)
