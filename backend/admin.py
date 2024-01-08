# backend/admin.py

from django.contrib import admin
from .models import CustomUser, UserActionLog, Client, Service, PasswordResetToken, Event, Alert

class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_time', 'action_type', 'permission', 'granted_by', 'granted_by_fullname')
    search_fields = ('user__email', 'action_type', 'granted_by__email', 'granted_by_fullname')

# Register your models with the admin site
admin.site.register(CustomUser)
admin.site.register(UserActionLog, UserActionLogAdmin)
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(PasswordResetToken)
admin.site.register(Event)
admin.site.register(Alert)
