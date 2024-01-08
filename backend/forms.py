# backend/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm


class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2', 'FirstName', 'LastName', 'NationalID', 'Address', 'BirthDate']
        # Include other fields from CustomUser that you want to appear in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

class CustomAdminAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        return self.cleaned_data['username']
