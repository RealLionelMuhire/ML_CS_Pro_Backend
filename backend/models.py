# backend/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.timezone import make_aware


class CustomUserManager(BaseUserManager):
    def create_user(self, email, FirstName, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, FirstName=FirstName, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, FirstName, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('NationalID', f'superuser_{get_random_string(length=10)}')

        return self.create_user(email, FirstName, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    UserID = models.AutoField(primary_key=True)
    UserRoles = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    FirstName = models.CharField(max_length=255, blank=True, null=True)
    LastName = models.CharField(max_length=255, blank=True, null=True)
    NationalID = models.CharField(max_length=25, unique=True)
    Address = models.CharField(max_length=150, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    registrarID = models.IntegerField(null=True, blank=True)
    registrarFirstName = models.CharField(max_length=255, null=True, blank=True)
    registrationDate = models.DateTimeField(auto_now_add=True)
    accessLevel = models.CharField(max_length=20, null=True, blank=True)
    BirthDate = models.DateField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)

    activatorID = models.IntegerField(null=True, blank=True)
    activatorEmail = models.EmailField(null=True, blank=True)
    activatorFirstName = models.CharField(max_length=255, null=True, blank=True)
    activationDate = models.DateTimeField(null=True, blank=True)

    deactivatorID = models.IntegerField(null=True, blank=True)
    deactivatorEmail = models.EmailField(null=True, blank=True)
    deactivatorFirstName = models.CharField(max_length=255, null=True, blank=True)
    deactivationDate = models.DateTimeField(null=True, blank=True)
    cv_file = models.URLField(blank=True, null=True)
    contract_file = models.URLField(blank=True, null=True)
    passport_file = models.URLField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['FirstName']

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True)

    def __str__(self):
        # Check if FirstName and LastName are present before formatting the string
        full_name = f"{self.FirstName} {self.LastName}" if self.FirstName and self.LastName else "N/A"
        return f"{full_name} - {self.email}"



def create_custom_permissions():
    permissions = [
        ('can_create_user', 'Can create user'),
        ('can_activate_user', 'Can activate user'),
        ('can_deactivate_user', 'Can deactivate user'),
        ('can_grant_permissions', 'Can grant permissions'),
    ]

    content_type = ContentType.objects.get_for_model(CustomUser)

    for codename, name in permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )

        if created:
            print(f'Permission {name} created successfully')
        else:
            print(f'Permission {name} already exists')

@receiver(post_migrate)
def on_post_migrate(sender, **kwargs):
    create_custom_permissions()

class UserActionLog(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    action_time = models.DateTimeField(default=timezone.now)
    action_type = models.CharField(max_length=20)  # e.g., 'Create User', 'Activate User', etc.
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)
    granted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_logs')
    granted_by_fullname = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set the user_id before saving
        if not self.user_id and self.user:
            self.user_id = self.user.UserID
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.action_type}"
class Client(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    taxResidency = models.CharField(max_length=255)
    tinNumber = models.CharField(max_length=50)
    citizenship = models.CharField(max_length=50)
    birthDate = models.DateField(null=True, blank=True)
    passportIdNumber = models.CharField(max_length=50, unique=True)
    countryOfIssue = models.CharField(max_length=50, null=True, blank=True)
    passportExpiryDate = models.DateField(null=True, blank=True)
    companyName = models.CharField(max_length=100, null=True, blank=True)
    sharePercent = models.CharField(max_length=255, null=True, blank=True)
    currentAddress = models.CharField(max_length=150, blank=True)
    clientContact = models.CharField(max_length=20)
    clientEmail = models.EmailField(unique=True)
    preferredLanguage = models.CharField(max_length=50)
    registrarID = models.IntegerField(null=True, blank=True)
    registrarEmail = models.EmailField(null=True, blank=True)
    registrarFirstName = models.CharField(max_length=255, null=True, blank=True)
    registrationDate = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    activatorID = models.IntegerField(null=True, blank=True)
    activatorEmail = models.EmailField(null=True, blank=True)
    activatorFirstName = models.CharField(max_length=255, null=True, blank=True)
    activationDate = models.DateField(null=True, blank=True)
    deactivatorID = models.IntegerField(null=True, blank=True)
    deactivatorEmail = models.EmailField(null=True, blank=True)
    deactivatorFirstName = models.CharField(max_length=255, null=True, blank=True)
    deactivationDate = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    introducerName = models.CharField(max_length=255, null=True, blank=True)
    introducerEmail = models.EmailField(null=True, blank=True)
    contactPersonName = models.CharField(max_length=255, null=True, blank=True)
    contactPersonEmail = models.EmailField(null=True, blank=True)
    contactPersonPhone = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return f"{self.firstName} {self.lastName}"


class Service(models.Model):
    initationDate = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    objective = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_elapsed_time = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    service_cost_per_hour = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='RWF')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    provider_id = models.IntegerField(null=True, blank=True)
    provider_email = models.EmailField(null=True, blank=True)
    provider_name = models.CharField(max_length=255, null=True, blank=True)
    serviced_client_id = models.IntegerField(null=True, blank=True)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    client_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.title

class PasswordResetToken(models.Model):
    resetDate = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    expiration_time = models.DateTimeField()

class Event(models.Model):
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Alert(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    action_taken = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    action_taken_description = models.TextField(blank=True, null=True)
    # Dates
    schedule_date = models.DateTimeField()
    set_date = models.DateTimeField()
    action_taken_date = models.DateTimeField(null=True, blank=True)
    expiration_date = models.DateTimeField()

    # Empty fields
    scheduler_name = models.CharField(max_length=255, blank=True)
    scheduler_email = models.EmailField(blank=True)

    client_name = models.CharField(max_length=255, blank=True)
    client_email = models.EmailField(blank=True)
    client_id = models.IntegerField(blank=True, null=True)

    setter_name = models.CharField(max_length=255, blank=True)
    setter_email = models.EmailField(blank=True)

    action_taker_name = models.CharField(max_length=255, blank=True)
    action_taker_email = models.EmailField(blank=True)

    # Relationships
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_alerts', blank=True, null=True)

    # Other related info that may be necessary
    # ...

    def __str__(self):
        return self.title

class Reservation(models.Model):
    timestamp = models.DateTimeField()
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    phone_contact = models.CharField(max_length=15)  # You may adjust the max_length according to your needs
    service_title = models.CharField(max_length=255)
    appointment_datetime = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Ensure that timestamp is formatted correctly before saving
        self.timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.appointment_datetime}"

class Options(models.Model):
    available_datetime = models.DateTimeField()
    day_of_week = models.CharField(max_length=10)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.available_datetime} - {self.status}"