# backend/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    UserID = models.AutoField(primary_key=True)
    UserType = models.CharField(max_length=20)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    FullName = models.CharField(max_length=255)
    NationalID = models.CharField(max_length=25, unique=True)
    Location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True)

    def __str__(self):
        return self.email

class RegistrationRequest(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admitted = models.BooleanField(default=False)
    admitted_email = models.EmailField(blank=True, null=True)
    admitted_full_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Registration Request for {self.full_name}"

class Client(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    tax_residency = models.CharField(max_length=255)
    tin = models.CharField(max_length=50)
    citizenship = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    passport_id_number = models.CharField(max_length=50, unique=True)
    country_of_issue = models.CharField(max_length=50)
    expiry_date = models.DateField()
    occupation = models.CharField(max_length=100)
    client_contact_phone = models.CharField(max_length=20)
    client_email = models.EmailField(unique=True)
    preferred_language = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name

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