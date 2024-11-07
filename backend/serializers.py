# backend/serializers.py
from rest_framework import serializers
from .models import CustomUser, Client, Service, Reports, Event, Alert, Reservation, UncompletedClient, WeeklyReport
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class UserSerializer(serializers.ModelSerializer):
    can_create_user = serializers.BooleanField(write_only=True, required=False)
    can_activate_user = serializers.BooleanField(write_only=True, required=False)
    can_deactivate_user = serializers.BooleanField(write_only=True, required=False)
    can_grant_permissions = serializers.BooleanField(write_only=True, required=False)
    registrarID = serializers.IntegerField(required=False)
    registrarName = serializers.CharField(max_length=255, required=False)
    # UserID = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', None)
        user_permissions_data = validated_data.pop('user_permissions', None)

        user = CustomUser.objects.create_user(**validated_data)

        if validated_data.get('can_create_user'):
            user.user_permissions.add(Permission.objects.get(codename='can_create_user'))
        if validated_data.get('can_activate_user'):
            user.user_permissions.add(Permission.objects.get(codename='can_activate_user'))
        if validated_data.get('can_deactivate_user'):
            user.user_permissions.add(Permission.objects.get(codename='can_deactivate_user'))
        if validated_data.get('can_grant_permissions'):
            user.user_permissions.add(Permission.objects.get(codename='can_grant_permissions'))

        return user

    def validate_UserID(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("UserID must be an integer.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field_name, value in representation.items():
            try:
                if field_name == 'UserID':
                    if not value or not str(value).isdigit():
                        representation['UserID'] = '0'  # Default valid value
                    else:
                        representation['UserID'] = int(value)  # Ensure UserID is an integer
            except Exception as e:
                return (f"Error processing field {field_name}: {e}")
        return representation

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

    def validate(self, attrs):
        # Skip validation for required fields on partial updates
        if self.instance and self.partial:
            attrs['tinNumber'] = attrs.get('tinNumber', self.instance.tinNumber)
        else:
            if not attrs.get('tinNumber'):
                raise serializers.ValidationError({"tinNumber": "This field may not be blank."})
        return attrs

class UpdateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ['tinNumber']

    def update(self, instance, validated_data):
        # Only update non-empty, non-null fields
        for attr, value in validated_data.items():
            if value not in ["", None]:
                setattr(instance, attr, value)
        instance.save()
        return instance
    
class UncompletedClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UncompletedClient
        fields = '__all__'

class UpdateUncompletedClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UncompletedClient
        exclude = ['clientEmail']

    def update(self, instance, validated_data):
        # Only update non-empty, non-null fields
        for attr, value in validated_data.items():
            if value not in ["", None]:
                setattr(instance, attr, value)
        instance.save()
        return instance

class ServiceSerializer(serializers.ModelSerializer):

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
        fields = ['UserID', 'UserRoles', 'email', 'contact', 'FirstName', 'LastName', 'NationalID', 'Address', 'registrarName', 'accessLevel', 'BirthDate']

class UserActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['isActive', 'is_staff', 'activatorID', 'activatorEmail', 'activatorFirstName', 'activationDate']
        read_only_fields = ['isActive', 'is_staff', 'activatorID', 'activatorEmail', 'activatorFirstName', 'activationDate']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'UserID', 'registrarID', 'registrarName', 'password', 'last_login', 
            'is_superuser', 'UserRoles', 'email', 'username', 'contact', 
            'FirstName', 'LastName', 'NationalID', 'Address', 'isActive', 
            'registrationDate', 'accessLevel', 'BirthDate', 'is_staff', 
            'countryOfResidence', 'is_active', 'tinNumber', 'taxResidency', 
            'citizenship', 'passportIdNumber', 'preferredLanguage', 'activatorID', 
            'activatorEmail', 'activatorFirstName', 'activationDate', 'deactivatorID', 
            'deactivatorEmail', 'deactivatorFirstName', 'deactivationDate', 
            'cv_link', 'contract_link', 'national_id_link', 'passport_link', 
            'registration_certificate_link', 'financialForecast', 'groups', 
            'user_permissions'
        ]
        # Make fields optional
        extra_kwargs = {
            'contact': {'required': False},
            'Address': {'required': False},
            'BirthDate': {'required': False},
            'FirstName': {'required': False},
            'LastName': {'required': False},
            'email': {'required': False},
            'national_id_link': {'required': False},
            'cv_link': {'required': False},
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


class ReportsSerializer(serializers.ModelSerializer):
    """
    Serializer for the Reports model.
    """

    class Meta:
        model = Reports
        fields = '__all__'


class ReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = [
            'title', 'description', 'report_link',
            'client_reportee_id', 'client_reportee_email', 'client_reportee_name'
        ]
        read_only_fields = ['reporter_id', 'reporter_email', 'reporter_name', 'created_at']

    def validate(self, data):
        if not any(data.values()):
            raise serializers.ValidationError("At least one field must be provided to update.")
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data.update({
            'user_id': self.user.UserID,
            'first_name': self.user.FirstName,
            'last_name': self.user.LastName,
            'user_roles': self.user.UserRoles,
        })

        return data

class WeeklyReportSerializer(serializers.ModelSerializer):
    """
    Serializer for the WeeklyReport model.
    """

    class Meta:
        model = WeeklyReport
        fields = '__all__'

class WeeklyReportUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReport
        fields = [
            'title', 'description', 'report_link',
            'client_reportee_id', 'client_reportee_email', 'client_reportee_name'
        ]
        read_only_fields = ['reporter_id', 'reporter_email', 'reporter_name', 'created_at']

    def validate(self, data):
        if not any(data.values()):
            raise serializers.ValidationError("At least one field must be provided to update.")
        return data
