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

        return self.create_user(email, FirstName, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    UserID = models.AutoField(primary_key=True)
    UserRoles = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    FirstName = models.CharField(max_length=255)
    LastName = models.CharField(max_length=255, blank=True, null=True)
    NationalID = models.CharField(max_length=25, unique=True)
    Address = models.CharField(max_length=100, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    isStaff = models.BooleanField(default=False, null=True, blank=True)
    registrarID = models.IntegerField(null=True, blank=True)
    registrarFirstName = models.CharField(max_length=255, null=True, blank=True)
    accessLevel = models.CharField(max_length=20, null=True, blank=True)
    BirthDate = models.DateField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True)

    def __str__(self):
        return self.email


def create_custom_permissions():
    permissions = [
        ('can_create_user', 'Can create user'),
        ('can_activate_user', 'Can activate user'),
        ('can_deactivate_user', 'Can deactivate user'),
        ('can_grant_permissions', 'Can grant permissions'),
        # more permissions if needed
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action_time = models.DateTimeField(default=timezone.now)
    action_type = models.CharField(max_length=20)  # e.g., 'Create User', 'Activate User', etc.
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, null=True, blank=True)
    granted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_logs')
    granted_by_fullname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.action_type}"

class Client(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    FirstName = models.CharField(max_length=255)
    LastName = models.CharField(max_length=255)
    taxResidency = models.CharField(max_length=255)
    tin = models.CharField(max_length=50)
    citizenship = models.CharField(max_length=50)
    dateOfBirth = models.DateField()
    placeOfBirth = models.CharField(max_length=100)
    passportIdNumber = models.CharField(max_length=50, unique=True)
    countryOfIssue = models.CharField(max_length=50)
    expiryDate = models.DateField()
    occupation = models.CharField(max_length=100)
    clientContactPhone = models.CharField(max_length=20)
    clientEmail = models.EmailField(unique=True)
    preferredLanguage = models.CharField(max_length=50)
    registrarID = models.IntegerField(null=True, blank=True)
    registrarEmail = models.EmailField(null=True, blank=True)
    registrarFirstName = models.CharField(max_length=255, null=True, blank=True)
    isActive = models.BooleanField(default=False, null=True, blank=True)
    activatorID = models.IntegerField(null=True, blank=True)
    activatorEmail = models.EmailField(unique=True, null=True, blank=True)
    activatorFirstName = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.FirstName} {self.LastName}"


class Action(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    objective = models.TextField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    total_elapsed_time = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

class PasswordResetToken(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    expiration_time = models.DateTimeField()