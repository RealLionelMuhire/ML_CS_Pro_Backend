from rest_framework.permissions import BasePermission

class IsSuperuserOrManagerAdmin(BasePermission):
    """
    Custom permission class to allow only superusers, managers, and admins to register users.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.accessLevel in ['manager', 'admin']