# backend/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'UserType', 'FullName', 'NationalID', 'Location']

class ClientRegistrationForm(UserCreationForm):
    ClientStatus = forms.CharField(max_length=20, required=True)
    ClientName = forms.CharField(max_length=100, required=True)
    CompanyName = forms.CharField(max_length=100, required=True)
    NationalID = forms.CharField(max_length=20, required=True)
    PassportNumber = forms.CharField(max_length=20, required=False)
    PassportExpirationDate = forms.DateField(required=False)
    TINNumber = forms.CharField(max_length=20, required=True)
    RegistrationIndexNumber = forms.CharField(max_length=20, required=True)
    OwnerShareholderID = forms.CharField(max_length=20, required=True)
    StageOfCompany = forms.CharField(max_length=50, required=True)
    CategoryOfCompany = forms.CharField(max_length=50, required=True)
    CopyOfIDOrPassport = forms.FileField(required=True)
    RegistrationCertificate = forms.FileField(required=True)
    TaxCertificate = forms.FileField(required=True)
    ProofOfResidence = forms.FileField(required=True)
    Shareholder = forms.FileField(required=True)
    Email = forms.EmailField(required=True)
    PhoneNumber = forms.CharField(max_length=20, required=True)
    Password = forms.CharField(widget=forms.PasswordInput, required=True)
