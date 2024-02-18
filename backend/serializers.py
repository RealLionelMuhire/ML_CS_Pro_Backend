# backend/serializers.py
from rest_framework import serializers
from .models import CustomUser, Client, Service, UserActionLog, Event, Alert, Reservation
from django.contrib.auth.models import Permission

class UserSerializer(serializers.ModelSerializer):
    # Your existing serializer fields

    can_create_user = serializers.BooleanField(write_only=True, required=False)
    can_activate_user = serializers.BooleanField(write_only=True, required=False)
    can_deactivate_user = serializers.BooleanField(write_only=True, required=False)
    can_grant_permissions = serializers.BooleanField(write_only=True, required=False)
    registrarID = serializers.IntegerField(required=False)
    registrarFirstName = serializers.CharField(max_length=255, required=False)
    cv_link = serializers.URLField(write_only=True, required=False)
    contract_link = serializers.URLField(write_only=True, required=False)
    passport_link = serializers.URLField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['UserID', 'UserRoles', 'email', 'FirstName', 'LastName','is_staff', 'NationalID', 'Address', 'isActive', 'can_create_user', 'can_activate_user', 'can_deactivate_user', 'can_grant_permissions', 'registrarID', 'registrarFirstName', 'accessLevel', 'BirthDate', 'cv_link', 'contract_link', 'passport_link']

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

class ServiceSerializer(serializers.ModelSerializer):
    # client_name = serializers.CharField(read_only=True)
    # client_email = serializers.EmailField(read_only=True)
    # provider_name = serializers.CharField(read_only=True)
    # provider_email = serializers.EmailField(read_only=True)

    class Meta:
        model = Service
        fields = [
            'id',
            'user',
            'title',
            'objective',
            'start_time',
            'end_time',
            'description',
            'is_active',
            'total_elapsed_time',
            'service_cost_per_hour',
            'currency',
            'total_cost',
            'provider_id',
            'provider_email',
            'provider_name',
            'serviced_client_id',
            'client_name',
            'client_email',
        ]
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['UserID', 'UserRoles', 'email', 'contact', 'FirstName', 'LastName', 'NationalID', 'Address', 'registrarFirstName', 'accessLevel', 'BirthDate']

class UserActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['isActive', 'is_staff', 'activatorID', 'activatorEmail', 'activatorFirstName', 'activationDate']
        read_only_fields = ['isActive', 'is_staff', 'activatorID', 'activatorEmail', 'activatorFirstName', 'activationDate']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['contact', 'Address', 'BirthDate', 'FirstName', 'LastName', 'email']
        # Make fields optional
        extra_kwargs = {
            'contact': {'required': False},
            'Address': {'required': False},
            'BirthDate': {'required': False},
            'FirstName': {'required': False},
            'LastName': {'required': False},
            'email': {'required': False},
        }

    def to_internal_value(self, data):
        # Skip validation for fields not present in the request data
        fields_to_skip = [key for key, value in data.items() if value == '']
        data = {key: value for key, value in data.items() if key not in fields_to_skip}
        return super().to_internal_value(data)
class CustomDateField(serializers.DateField):
    def to_representation(self, value):
        # Format the datetime value as "day-month-year"
        return value.date() if value else None

class AlertSerializer(serializers.ModelSerializer):
    schedule_date = CustomDateField()
    expiration_date = CustomDateField()
    set_date = CustomDateField(required=False)
    action_taken_date = CustomDateField(required=False)

    class Meta:
        model = Alert
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Reservation model.
    """

    class Meta:
        model = Reservation
        fields = '__all__'
