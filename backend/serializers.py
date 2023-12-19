# backend/serializers.py
from rest_framework import serializers
from .models import CustomUser, Client, Action, UserActionLog
from django.contrib.auth.models import Permission

class UserSerializer(serializers.ModelSerializer):
    # Your existing serializer fields

    can_create_user = serializers.BooleanField(write_only=True, required=False)
    can_activate_user = serializers.BooleanField(write_only=True, required=False)
    can_deactivate_user = serializers.BooleanField(write_only=True, required=False)
    can_grant_permissions = serializers.BooleanField(write_only=True, required=False)
    registered_by_id = serializers.IntegerField(required=False)
    registered_by_fullname = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = CustomUser
        fields = ['UserID', 'UserRoles', 'username', 'email', 'FirstName', 'LastName', 'NationalID', 'Address', 'is_active', 'is_staff', 'can_create_user', 'can_activate_user', 'can_deactivate_user', 'can_grant_permissions', 'registered_by_id', 'registered_by_fullname']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)

        # Handle custom permissions
        if validated_data.get('can_create_user'):
            user.user_permissions.add(Permission.objects.get(codename='can_create_user'))
            UserActionLog.objects.create(user=user, action_type='Create User', permission=user.user_permissions.last())
        if validated_data.get('can_activate_user'):
            user.user_permissions.add(Permission.objects.get(codename='can_activate_user'))
            UserActionLog.objects.create(user=user, action_type='Activate User', permission=user.user_permissions.last())
        if validated_data.get('can_deactivate_user'):
            user.user_permissions.add(Permission.objects.get(codename='can_deactivate_user'))
            UserActionLog.objects.create(user=user, action_type='Deactivate User', permission=user.user_permissions.last())
        if validated_data.get('can_grant_permissions'):
            user.user_permissions.add(Permission.objects.get(codename='can_grant_permissions'))
            UserActionLog.objects.create(user=user, action_type='Grant Permissions', permission=user.user_permissions.last())

        return user

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ActionSerializer(serializers.ModelSerializer):
    elapsed_time = serializers.SerializerMethodField()
    sum_elapsed_time = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Action
        fields = ['title', 'objective', 'start_time', 'end_time', 'description', 'is_active', 'elapsed_time', 'sum_elapsed_time']
        extra_kwargs = {
            'sum_elapsed_time': {'write_only': True},
        }

    def get_elapsed_time(self, obj):
        start_time = obj.start_time
        end_time = obj.end_time

        if start_time and end_time:
            elapsed_time_minutes = (end_time - start_time).total_seconds() / 60
            return elapsed_time_minutes
        return None

