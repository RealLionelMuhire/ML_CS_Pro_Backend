from rest_framework.permissions import BasePermission

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