from rest_framework.permissions import BasePermission
from .models import CustomUser, Client

class IsSuperuserOrManagerAdmin(BasePermission):
    """
    Custom permission class to allow only superusers, managers, and admins to register and modify other users.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.accessLevel in ['manager', 'admin']

class IsUser(BasePermission):
    """
    Custom permission class for all users not client.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.accessLevel in ['manager', 'admin', 'user']

class IsSuperuserOrManagerAdminOrReadOnly(BasePermission):
    """
    Custom permission class to allow only superusers, managers, and admins to register and modify other users.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.accessLevel in ['manager', 'admin'] or request.method in ['GET', 'HEAD', 'OPTIONS']

class IsClient(BasePermission):
    """
    Custom permission for clients.
    """

    def has_permission(self, request, view):
        return request.user.accessLevel in ['Client']

class IsClientActivated(BasePermission):
    """
    Custom permission to check if a user is an activated client.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user type is "Client"
        if request.user.accessLevel != 'Client':
            return False

        # Get the user's ID and Tin number
        user_id = request.user.UserID
        user_tin_number = request.user.tinNumber

        # Check if there's a corresponding client with the same registrar ID and Tin number
        try:
            client = Client.objects.get(registrarID=user_id, tinNumber=user_tin_number)
            # Check if the client is active
            if client.isActive:
                return True
        except Client.DoesNotExist:
            pass

        return False