# custom_user_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Permission
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from rest_framework import status
from ..models import CustomUser, UserActionLog

class UserPermissionsView(APIView):
    """
    API view to retrieve the permissions of the authenticated user.
    Endpoint: GET /user-permissions/
    """
    def get(self, request):
        """Handle GET requests and return the permissions of the authenticated user."""
        user_permissions = request.user.user_permissions.all()
        permission_names = [permission.name for permission in user_permissions]
        return Response({'user_permissions': permission_names})

class AllPermissionsView(APIView):
    """
    API view to retrieve all available permissions.
    Endpoint: GET /all-permissions/
    """
    def get(self, request):
        """Handle GET requests and return all available permissions."""
        all_permissions = Permission.objects.all()
        permission_names = [permission.name for permission in all_permissions]
        return Response({'all_permissions': permission_names})

class ActivateUserView(APIView):
    """
    API view to activate a user.
    Requires 'auth.can_activate_user' permission.
    Endpoint: POST /activate-user/<int:user_id>/
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required('auth.can_activate_user', raise_exception=True))
    @require_POST
    def post(self, request, user_id):
        """Handle POST requests to activate a user."""
        try:
            user = CustomUser.objects.get(pk=user_id)
            
            if not user.is_active:
                user.is_active = True
                user.save()
                UserActionLog.objects.create(user=user, action_type='Activate User', permission=user.user_permissions.last(), granted_by=request.user, granted_by_fullname=request.user.FullName)
                return Response({'message': 'User activated successfully. Welcome email sent.'})
            else:
                return Response({'message': 'User is already activated.'})
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class DeactivateUserView(APIView):
    """
    API view to deactivate a user.
    Requires 'auth.can_deactivate_user' permission.
    Endpoint: POST /deactivate-user/<int:user_id>/
    """
    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required('auth.can_deactivate_user', raise_exception=True))
    @require_POST
    def post(self, request, user_id):
        """Handle POST requests to deactivate a user."""
        try:
            user = CustomUser.objects.get(pk=user_id)
            if user.is_active:
                user.is_active = False
                user.save()
                UserActionLog.objects.create(user=user, action_type='Deactivate User', permission=user.user_permissions.last(), granted_by=request.user, granted_by_fullname=request.user.FullName)
                return Response({'message': 'User Deactivated successfully'})
            else:
                return Response({'message': 'User is already deactivated.'})
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class GrantPermissionsView(APIView):
    """
    API view to grant permissions to a user.
    Requires 'auth.can_grant_permissions' permission.
    Endpoint: POST /grant-permissions/<int:user_id>/
    """

    permission_classes = [IsAuthenticated]

    @method_decorator(permission_required('auth.can_grant_permissions', raise_exception=True))
    @require_POST
    def post(self, request, user_id):
        """Handle POST requests to grant permissions to a user."""
        try:
            if not request.user.has_perm('auth.can_grant_permissions'):
                return Response({'message': 'Permission denied. You do not have the required permission to grant permissions.'}, status=status.HTTP_403_FORBIDDEN)

            user_to_grant = CustomUser.objects.get(pk=user_id)

            if not request.user.has_perm('auth.can_grant_permissions'):
                return Response({'message': 'Permission denied. You do not have the required permission to grant the specified permissions.'}, status=status.HTTP_403_FORBIDDEN)

            user_to_grant.user_permissions.add(Permission.objects.get(codename='can_create_user'))
            user_to_grant.user_permissions.add(Permission.objects.get(codename='can_activate_user'))
            user_to_grant.user_permissions.add(Permission.objects.get(codename='can_deactivate_user'))

            UserActionLog.objects.create(user=user_to_grant, action_type='Grant Permissions', granted_by=request.user)
            
            return Response({'message': 'Permissions granted successfully'})
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
