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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, FirstName, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        extra_fields.setdefault('is_active', True)
        
        # Extract custom fields
        can_create_user = extra_fields.pop('can_create_user', False)
        can_activate_user = extra_fields.pop('can_activate_user', False)
        can_deactivate_user = extra_fields.pop('can_deactivate_user', False)
        can_grant_permissions = extra_fields.pop('can_grant_permissions', False)

        email = self.normalize_email(email)
        user = self.model(email=email, FirstName=FirstName, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Handle custom permissions
        if can_create_user:
            user.user_permissions.add(Permission.objects.get(codename='can_create_user'))
        if can_activate_user:
            user.user_permissions.add(Permission.objects.get(codename='can_activate_user'))
        if can_deactivate_user:
            user.user_permissions.add(Permission.objects.get(codename='can_deactivate_user'))
        if can_grant_permissions:
            user.user_permissions.add(Permission.objects.get(codename='can_grant_permissions'))

        return user

    def create_superuser(self, email, FirstName, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('NationalID', f'superuser_{get_random_string(length=10)}')

        # Create the user first
        user = self.create_user(email, FirstName, password, **extra_fields)

        # Set registrarID to be the same as UserID
        user.registrarID = user.UserID
        user.save(using=self._db)

        # Debugging: Print user ID and registrar ID for confirmation
        print(f"Superuser created with UserID: {user.UserID}, registrarID: {user.registrarID}")

        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    UserID = models.AutoField(primary_key=True)
    UserRoles = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    FirstName = models.CharField(max_length=255, blank=True, null=True)
    LastName = models.CharField(max_length=255, blank=True, null=True)
    NationalID = models.CharField(max_length=35, blank=True, null=True)
    Address = models.CharField(max_length=150, blank=True)
    isActive = models.BooleanField(default=True)
    registrarID = models.CharField(max_length=25)
    registrarName = models.CharField(max_length=255)
    registrationDate = models.DateTimeField(auto_now_add=True)
    accessLevel = models.CharField(max_length=20, blank=True, null=True)
    BirthDate = models.DateField(null=True, blank=True)
    is_staff = models.BooleanField(default=False, blank=True, null=True)
    countryOfResidence = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)


    tinNumber = models.CharField(max_length=50, null=True, blank=True)
    taxResidency = models.CharField(max_length=255, null=True, blank=True)
    citizenship = models.CharField(max_length=50, null=True, blank=True)
    passportIdNumber = models.CharField(max_length=50, null=True, blank=True)
    preferredLanguage = models.CharField(max_length=50, null=True, blank=True)




    activatorID = models.IntegerField(null=True, blank=True)
    activatorEmail = models.EmailField(null=True, blank=True)
    activatorFirstName = models.CharField(max_length=255, null=True, blank=True)
    activationDate = models.DateTimeField(null=True, blank=True)

    deactivatorID = models.IntegerField(null=True, blank=True)
    deactivatorEmail = models.EmailField(null=True, blank=True)
    deactivatorFirstName = models.CharField(max_length=255, null=True, blank=True)
    deactivationDate = models.DateTimeField(null=True, blank=True)
    
    cv_link = models.JSONField(blank=True, null=True)
    contract_link = models.JSONField(blank=True, null=True)
    national_id_link = models.JSONField(blank=True, null=True)
    passport_link = models.URLField(blank=True, null=True)
    registration_certificate_link = models.URLField(blank=True, null=True)
    other_docs_link = models.JSONField(blank=True, null=True)

    financialForecast = models.JSONField(null=True, blank=True)
    

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['FirstName']

    groups = models.ManyToManyField('auth.Group', related_name='customci_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True)

    def __str__(self):
        # Check if FirstName and LastName are present before formatting the string
        full_name = f"{self.FirstName} {self.LastName}" if self.FirstName and self.LastName else "N/A"
        return f"{full_name} - {self.email}"


class Transaction(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expiration_time = models.DateTimeField()

    def __str__(self):
        return f"Transaction for {self.user.email}"


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
    firstName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=True, null=True)
    taxResidency = models.CharField(max_length=255, blank=True, null=True)
    tinNumber = models.CharField(max_length=50, unique=True)
    citizenship = models.CharField(max_length=50, blank=True, null=True)
    birthDate = models.DateField(null=True, blank=True)
    countryOfResidence = models.CharField(max_length=50, null=True, blank=True)
    passportIdNumber = models.CharField(max_length=50, null=True, blank=True)
    countryOfIssue = models.CharField(max_length=50, null=True, blank=True)
    passportIdNumber = models.CharField(max_length=50, null=True, blank=True)
    NameOfEntity = models.CharField(max_length=100, null=True, blank=True)
    PrevNameOfEntity = models.CharField(max_length=100, null=True, blank=True)
    TypeOfEntity = models.CharField(max_length=100, null=True, blank=True)
    TypeOfLicense = models.CharField(max_length=100, null=True, blank=True)
    sharePercent = models.CharField(max_length=255, null=True, blank=True)
    currentAddress = models.CharField(max_length=150, blank=True)
    clientContact = models.CharField(max_length=20, blank=True, null=True)
    clientEmail = models.EmailField(blank=True, null=True)
    preferredLanguage = models.CharField(max_length=50, blank=True, null=True)
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
    NationalID = models.CharField(max_length=50, null=True, blank=True)
    
    introducerName = models.CharField(max_length=255, null=True, blank=True)
    introducerEmail = models.EmailField(null=True, blank=True)
    
    contactPersonName = models.CharField(max_length=255, null=True, blank=True)
    contactPersonEmail = models.EmailField(null=True, blank=True)
    contactPersonPhone = models.CharField(max_length=20, null=True, blank=True)

    authorisedName = models.CharField(max_length=255, null=True, blank=True)
    authorisedEmail = models.EmailField(null=True, blank=True)
    authorisedPersonContact = models.CharField(max_length=20, null=True, blank=True)
    authorisedCurrentAddress = models.CharField(max_length=255, null=True, blank=True)
    authorisedRelationship = models.CharField(max_length=255, null=True, blank=True)

    CathegoryOfEntity = models.CharField(max_length=255, null=True, blank=True)
    SPVType = models.CharField(max_length=255, null=True, blank=True)
    SectorOfEntity = models.CharField(max_length=255, null=True, blank=True)
    OtherSectorOfEntity = models.CharField(max_length=255, null=True, blank=True)


    isPep = models.CharField(max_length=5, null=True, blank=True)

    registration_certificate_link = models.URLField(blank=True, null=True)
    signature_link = models.URLField(blank=True, null=True)
    bankStatement_link = models.URLField(blank=True, null=True)
    professionalReference_link = models.URLField(blank=True, null=True)
    national_id_link = models.URLField(blank=True, null=True)
    passport_link = models.URLField(blank=True, null=True)

    incorporationDate = models.DateField(null=True, blank=True)
    countryOfIncorporation = models.CharField(max_length=50, null=True, blank=True)
    registeredOfficeAddress = models.CharField(max_length=255, null=True, blank=True)
    businessActivity = models.CharField(max_length=255, null=True, blank=True)
    countryOfOperation = models.CharField(max_length=50, null=True, blank=True)

    changeName = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsName = models.CharField(max_length=55, null=True, blank=True)
    financialServicesBusiness = models.CharField(max_length=55, null=True, blank=True)
    jurisdictionName = models.CharField(max_length=55, null=True, blank=True)
    jurisdictionAddress = models.CharField(max_length=55, null=True, blank=True)
    similarApplication = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsPartner = models.CharField(max_length=55, null=True, blank=True)
    criticised = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsJurisdictions = models.CharField(max_length=55, null=True, blank=True)

    bankruptcyApplication = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsForfeit = models.CharField(max_length=55, null=True, blank=True)
    receiverAppointed = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsReceiver = models.CharField(max_length=55, null=True, blank=True)
    civilProceedings = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsFinancial = models.CharField(max_length=55, null=True, blank=True)
    convicted = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsOffence = models.CharField(max_length=55, null=True, blank=True)
    directorConvicted = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsDirector = models.CharField(max_length=55, null=True, blank=True)

    RemittingParty = models.CharField(max_length=55, null=True, blank=True)
    ModeOfPayment = models.CharField(max_length=55, null=True, blank=True)
    RelationshipWithApplicant = models.CharField(max_length=55, null=True, blank=True)
    ProposedNameOption1 = models.CharField(max_length=55, null=True, blank=True)
    ProposedNameOption2 = models.CharField(max_length=55, null=True, blank=True)
    ProposedNameOption3 = models.CharField(max_length=55, null=True, blank=True)

    proposedActivity = models.CharField(max_length=55, null=True, blank=True)
    targetSectors = models.CharField(max_length=55, null=True, blank=True)
    targetedCountries = models.CharField(max_length=55, null=True, blank=True)
    specialLicense = models.CharField(max_length=55, null=True, blank=True)
    secretary = models.CharField(max_length=55, null=True, blank=True)
    productService = models.CharField(max_length=55, null=True, blank=True)
    businessAddress = models.CharField(max_length=55, null=True, blank=True)

    sharesType = models.CharField(max_length=55, null=True, blank=True)
    sharesNumber = models.CharField(max_length=55, null=True, blank=True)
    statedCapital = models.CharField(max_length=55, null=True, blank=True)

    sourceOfFunds = models.CharField(max_length=155, null=True, blank=True)
    otherSourceOfFunds = models.CharField(max_length=55, null=True, blank=True)
    countrySourceFunds = models.CharField(max_length=55, null=True, blank=True)
    netAnnualIncome = models.CharField(max_length=55, null=True, blank=True)
    estimatedNetWorth = models.CharField(max_length=55, null=True, blank=True)
    sourceOfWealth = models.CharField(max_length=155, null=True, blank=True)
    otherSourceOfWealth = models.CharField(max_length=55, null=True, blank=True)
    countrySourceWealth = models.CharField(max_length=55, null=True, blank=True)
    bankInvolvedWealth = models.CharField(max_length=55, null=True, blank=True)

    isMlDirectors = models.CharField(max_length=55, null=True, blank=True)
    Director1FirstName = models.CharField(max_length=55, null=True, blank=True)
    Director1LastName = models.CharField(max_length=55, null=True, blank=True)
    Director1email = models.EmailField(null=True, blank=True)
    Director1contact = models.CharField(max_length=55, null=True, blank=True)
    Director1BirthDate = models.DateField(null=True, blank=True)
    Director1NationalID = models.CharField(max_length=55, null=True, blank=True)
    Director1passportIdNumber = models.CharField(max_length=55, null=True, blank=True)
    Director1countryOfIssue = models.CharField(max_length=55, null=True, blank=True)
    Director1passportExpiryDate = models.DateField(null=True, blank=True)
    Director1citizenship = models.CharField(max_length=55, null=True, blank=True)
    Director1specifiedCitizenship = models.CharField(max_length=55, null=True, blank=True)
    Director1countryOfResidence = models.CharField(max_length=55, null=True, blank=True)
    Director1preferredLanguage = models.CharField(max_length=55, null=True, blank=True)
    Director1NameOfEntity = models.CharField(max_length=55, null=True, blank=True)
    Director1tinNumber = models.CharField(max_length=55, null=True, blank=True)
    Director1taxResidency = models.CharField(max_length=55, null=True, blank=True)

    Director2FirstName = models.CharField(max_length=55, null=True, blank=True)
    Director2LastName = models.CharField(max_length=55, null=True, blank=True)
    Director2email = models.EmailField(null=True, blank=True)
    Director2contact = models.CharField(max_length=55, null=True, blank=True)
    Director2BirthDate = models.DateField(null=True, blank=True)
    Director2NationalID = models.CharField(max_length=55, null=True, blank=True)
    Director2passportIdNumber = models.CharField(max_length=55, null=True, blank=True)
    Director2countryOfIssue = models.CharField(max_length=55, null=True, blank=True)
    Director2passportExpiryDate = models.DateField(null=True, blank=True)
    Director2citizenship = models.CharField(max_length=55, null=True, blank=True)
    Director2specifiedCitizenship = models.CharField(max_length=55, null=True, blank=True)
    Director2countryOfResidence = models.CharField(max_length=55, null=True, blank=True)
    Director2preferredLanguage = models.CharField(max_length=55, null=True, blank=True)
    Director2NameOfEntity = models.CharField(max_length=55, null=True, blank=True)
    Director2tinNumber = models.CharField(max_length=55, null=True, blank=True)
    Director2taxResidency = models.CharField(max_length=55, null=True, blank=True)

    Director3FirstName = models.CharField(max_length=55, null=True, blank=True)
    Director3LastName = models.CharField(max_length=55, null=True, blank=True)
    Director3email = models.EmailField(null=True, blank=True)
    Director3contact = models.CharField(max_length=55, null=True, blank=True)
    Director3BirthDate = models.DateField(null=True, blank=True)
    Director3NationalID = models.CharField(max_length=55, null=True, blank=True)
    Director3passportIdNumber = models.CharField(max_length=55, null=True, blank=True)
    Director3countryOfIssue = models.CharField(max_length=55, null=True, blank=True)
    Director3passportExpiryDate = models.DateField(null=True, blank=True)
    Director3citizenship = models.CharField(max_length=55, null=True, blank=True)
    Director3specifiedCitizenship = models.CharField(max_length=55, null=True, blank=True)
    Director3countryOfResidence = models.CharField(max_length=55, null=True, blank=True)
    Director3preferredLanguage = models.CharField(max_length=55, null=True, blank=True)
    Director3NameOfEntity = models.CharField(max_length=55, null=True, blank=True)
    Director3tinNumber = models.CharField(max_length=55, null=True, blank=True)
    Director3taxResidency = models.CharField(max_length=55, null=True, blank=True)

    Director1isPep = models.CharField(max_length=55, null=True, blank=True)
    Director2isPep = models.CharField(max_length=55, null=True, blank=True)
    Director3isPep = models.CharField(max_length=55, null=True, blank=True)

    bankName = models.CharField(max_length=55, null=True, blank=True)
    Currency = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory1 = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory2 = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory3 = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory4 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory1 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory2 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory3 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory4 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser1 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser1AccessRights = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser2 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser2AccessRights = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser3 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser3AccessRights = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser4 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser4AccessRights = models.CharField(max_length=55, null=True, blank=True)
    modeOfOperation = models.CharField(max_length=55, null=True, blank=True)
    callBackProcessContact = models.CharField(max_length=55, null=True, blank=True)
    nameOfProposedOfficer = models.CharField(max_length=55, null=True, blank=True)

    registration_certificate_link = models.JSONField(blank=True, null=True)
    signature_link = models.JSONField(blank=True, null=True)
    bankStatement_link = models.JSONField(blank=True, null=True)
    professionalReference_link = models.JSONField(blank=True, null=True)
    national_id_link = models.JSONField(blank=True, null=True)
    passport_link = models.JSONField(blank=True, null=True)
    confirmationLetter_link = models.JSONField(blank=True, null=True)
    custody_accounts_link = models.JSONField(blank=True, null=True)
    source_of_funds_link = models.JSONField(blank=True, null=True)
    payslips_link = models.JSONField(blank=True, null=True)
    due_diligence_link = models.JSONField(blank=True, null=True)
    financial_statements_link = models.JSONField(blank=True, null=True)
    proof_of_ownership_link = models.JSONField(blank=True, null=True)
    lease_agreement_link = models.JSONField(blank=True, null=True)
    documentary_evidence_link = models.JSONField(blank=True, null=True)
    bank_statement_proceeds_link = models.JSONField(blank=True, null=True)
    bank_statement_link = models.JSONField(blank=True, null=True)
    cdd_documents_link = models.JSONField(blank=True, null=True)
    bank_statements_link = models.JSONField(blank=True, null=True)
    bank_statements_proceeds_link = models.JSONField(blank=True, null=True)
    notarised_documents_link = models.JSONField(blank=True, null=True)
    letter_from_donor_link = models.JSONField(blank=True, null=True)
    donor_source_of_wealth_link = models.JSONField(blank=True, null=True)
    donor_bank_statement_link = models.JSONField(blank=True, null=True)
    letter_from_relevant_org_link = models.JSONField(blank=True, null=True)
    lottery_bank_statement_link = models.JSONField(blank=True, null=True)
    creditor_agreement_link = models.JSONField(blank=True, null=True)
    creditor_cdd_link = models.JSONField(blank=True, null=True)
    creditor_bank_statement_link = models.JSONField(blank=True, null=True)
    legal_document_link = models.JSONField(blank=True, null=True)
    notary_letter_link = models.JSONField(blank=True, null=True)
    executor_letter_link = models.JSONField(blank=True, null=True)
    loan_agreement_link = models.JSONField(blank=True, null=True)
    loan_bank_statement_link = models.JSONField(blank=True, null=True)
    related_third_party_loan_agreement_link = models.JSONField(blank=True, null=True)
    related_third_party_cdd_link = models.JSONField(blank=True, null=True)
    related_third_party_bank_statement_link = models.JSONField(blank=True, null=True)
    unrelated_third_party_loan_agreement_link = models.JSONField(blank=True, null=True)
    unrelated_third_party_cdd_link = models.JSONField(blank=True, null=True)
    unrelated_third_party_bank_statement_link = models.JSONField(blank=True, null=True)
    signed_letter_from_notary_link = models.JSONField(blank=True, null=True)
    property_contract_link = models.JSONField(blank=True, null=True)
    insurance_pay_out_link = models.JSONField(blank=True, null=True)
    retirement_annuity_fund_statement_link = models.JSONField(blank=True, null=True)
    passport_link = models.JSONField(blank=True, null=True)
    utility_link = models.JSONField(blank=True, null=True)
    wealth_link = models.JSONField(blank=True, null=True)
    cv_link = models.JSONField(blank=True, null=True)
    funds_link = models.JSONField(blank=True, null=True)
    source_of_wealth_link = models.JSONField(blank=True, null=True)
    principals_identification_link = models.JSONField(blank=True, null=True)
    shareholders_link = models.JSONField(blank=True, null=True)
    declaration_of_trust_link = models.JSONField(blank=True, null=True)
    certificate_of_registration_link = models.JSONField(blank=True, null=True)
    deed_of_retirement_link = models.JSONField(blank=True, null=True)
    business_plan_link = models.JSONField(blank=True, null=True)
    registered_office_link = models.JSONField(blank=True, null=True)
    register_of_trustee_link = models.JSONField(blank=True, null=True)
    proof_of_source_of_funds_link = models.JSONField(blank=True, null=True)
    proof_of_source_of_wealth_link = models.JSONField(blank=True, null=True)
    latest_accounts_or_bank_statements_link = models.JSONField(blank=True, null=True)
    licence_link = models.JSONField(blank=True, null=True)
    certificate_of_incumbency_link = models.JSONField(blank=True, null=True)
    charter_link = models.JSONField(blank=True, null=True)
    latest_accounts_link = models.JSONField(blank=True, null=True)
    principals_foundation_link = models.JSONField(blank=True, null=True)
    financialForecast = models.JSONField(null=True, blank=True)
    other_necessary_documents_link = models.JSONField(null=True, blank=True)
    expectedAccountActivity = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f"{self.firstName} {self.lastName}"

class UncompletedClient(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    firstName = models.CharField(max_length=255, null=True, blank=True)
    lastName = models.CharField(max_length=255, null=True, blank=True)
    taxResidency = models.CharField(max_length=255, null=True, blank=True)
    tinNumber = models.CharField(max_length=50, null=True, blank=True)
    citizenship = models.CharField(max_length=50, null=True, blank=True)
    birthDate = models.DateField(null=True, blank=True)
    countryOfResidence = models.CharField(max_length=50, null=True, blank=True)
    passportIdNumber = models.CharField(max_length=50, null=True, blank=True)
    countryOfIssue = models.CharField(max_length=50, null=True, blank=True)
    passportExpiryDate = models.DateField(null=True, blank=True)
    NameOfEntity = models.CharField(max_length=100, null=True, blank=True)
    PrevNameOfEntity = models.CharField(max_length=100, null=True, blank=True)
    TypeOfEntity = models.CharField(max_length=100, null=True, blank=True)
    TypeOfLicense = models.CharField(max_length=100, null=True, blank=True)
    sharePercent = models.CharField(max_length=255, null=True, blank=True)
    currentAddress = models.CharField(max_length=150, blank=True)
    clientContact = models.CharField(max_length=20, blank=True)
    clientEmail = models.EmailField(unique=True, blank=True, null=True)
    preferredLanguage = models.CharField(max_length=50, blank=True)
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
    NationalID = models.CharField(max_length=255, null=True, blank=True)

    CathegoryOfEntity = models.CharField(max_length=255, null=True, blank=True)
    SPVType = models.CharField(max_length=255, null=True, blank=True)
    SectorOfEntity = models.CharField(max_length=255, null=True, blank=True)
    OtherSectorOfEntity = models.CharField(max_length=255, null=True, blank=True)
    
    introducerName = models.CharField(max_length=255, null=True, blank=True)
    introducerEmail = models.EmailField(null=True, blank=True)
    
    contactPersonName = models.CharField(max_length=255, null=True, blank=True)
    contactPersonEmail = models.EmailField(null=True, blank=True)
    contactPersonPhone = models.CharField(max_length=20, null=True, blank=True)

    authorisedName = models.CharField(max_length=255, null=True, blank=True)
    authorisedEmail = models.EmailField(null=True, blank=True)
    authorisedPersonContact = models.CharField(max_length=20, null=True, blank=True)
    authorisedCurrentAddress = models.CharField(max_length=255, null=True, blank=True)
    authorisedRelationship = models.CharField(max_length=255, null=True, blank=True)

    isPep = models.CharField(max_length=5, null=True, blank=True)

    incorporationDate = models.DateField(null=True, blank=True)
    countryOfIncorporation = models.CharField(max_length=50, null=True, blank=True)
    registeredOfficeAddress = models.CharField(max_length=255, null=True, blank=True)
    businessActivity = models.CharField(max_length=255, null=True, blank=True)
    countryOfOperation = models.CharField(max_length=50, null=True, blank=True)

    changeName = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsName = models.CharField(max_length=55, null=True, blank=True)
    financialServicesBusiness = models.CharField(max_length=55, null=True, blank=True)
    jurisdictionName = models.CharField(max_length=55, null=True, blank=True)
    jurisdictionAddress = models.CharField(max_length=55, null=True, blank=True)
    similarApplication = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsPartner = models.CharField(max_length=55, null=True, blank=True)
    criticised = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsJurisdictions = models.CharField(max_length=55, null=True, blank=True)

    bankruptcyApplication = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsForfeit = models.CharField(max_length=55, null=True, blank=True)
    receiverAppointed = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsReceiver = models.CharField(max_length=55, null=True, blank=True)
    civilProceedings = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsFinancial = models.CharField(max_length=55, null=True, blank=True)
    convicted = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsOffence = models.CharField(max_length=55, null=True, blank=True)
    directorConvicted = models.CharField(max_length=55, null=True, blank=True)
    similarApplicationDetailsDirector = models.CharField(max_length=55, null=True, blank=True)

    RemittingParty = models.CharField(max_length=55, null=True, blank=True)
    ModeOfPayment = models.CharField(max_length=55, null=True, blank=True)
    RelationshipWithApplicant = models.CharField(max_length=55, null=True, blank=True)
    ProposedNameOption1 = models.CharField(max_length=55, null=True, blank=True)
    ProposedNameOption2 = models.CharField(max_length=55, null=True, blank=True)
    ProposedNameOption3 = models.CharField(max_length=55, null=True, blank=True)

    proposedActivity = models.CharField(max_length=55, null=True, blank=True)
    targetSectors = models.CharField(max_length=55, null=True, blank=True)
    targetedCountries = models.CharField(max_length=55, null=True, blank=True)
    specialLicense = models.CharField(max_length=55, null=True, blank=True)
    secretary = models.CharField(max_length=55, null=True, blank=True)
    productService = models.CharField(max_length=55, null=True, blank=True)
    businessAddress = models.CharField(max_length=55, null=True, blank=True)

    sharesType = models.CharField(max_length=55, null=True, blank=True)
    sharesNumber = models.CharField(max_length=55, null=True, blank=True)
    statedCapital = models.CharField(max_length=55, null=True, blank=True)


    sourceOfFunds = models.CharField(max_length=155, null=True, blank=True)
    otherSourceOfFunds = models.CharField(max_length=55, null=True, blank=True)
    countrySourceFunds = models.CharField(max_length=55, null=True, blank=True)
    netAnnualIncome = models.CharField(max_length=55, null=True, blank=True)
    estimatedNetWorth = models.CharField(max_length=55, null=True, blank=True)
    sourceOfWealth = models.CharField(max_length=155, null=True, blank=True)
    otherSourceOfWealth = models.CharField(max_length=55, null=True, blank=True)
    countrySourceWealth = models.CharField(max_length=55, null=True, blank=True)
    bankInvolvedWealth = models.CharField(max_length=55, null=True, blank=True)

    isMlDirectors = models.CharField(max_length=55, null=True, blank=True)
    Director1FirstName = models.CharField(max_length=55, null=True, blank=True)
    Director1LastName = models.CharField(max_length=55, null=True, blank=True)
    Director1email = models.EmailField(null=True, blank=True)
    Director1contact = models.CharField(max_length=55, null=True, blank=True)
    Director1BirthDate = models.DateField(null=True, blank=True)
    Director1NationalID = models.CharField(max_length=55, null=True, blank=True)
    Director1passportIdNumber = models.CharField(max_length=55, null=True, blank=True)
    Director1countryOfIssue = models.CharField(max_length=55, null=True, blank=True)
    Director1passportExpiryDate = models.DateField(null=True, blank=True)
    Director1citizenship = models.CharField(max_length=55, null=True, blank=True)
    Director1specifiedCitizenship = models.CharField(max_length=55, null=True, blank=True)
    Director1countryOfResidence = models.CharField(max_length=55, null=True, blank=True)
    Director1preferredLanguage = models.CharField(max_length=55, null=True, blank=True)
    Director1NameOfEntity = models.CharField(max_length=55, null=True, blank=True)
    Director1tinNumber = models.CharField(max_length=55, null=True, blank=True)
    Director1taxResidency = models.CharField(max_length=55, null=True, blank=True)

    Director2FirstName = models.CharField(max_length=55, null=True, blank=True)
    Director2LastName = models.CharField(max_length=55, null=True, blank=True)
    Director2email = models.EmailField(null=True, blank=True)
    Director2contact = models.CharField(max_length=55, null=True, blank=True)
    Director2BirthDate = models.DateField(null=True, blank=True)
    Director2NationalID = models.CharField(max_length=55, null=True, blank=True)
    Director2passportIdNumber = models.CharField(max_length=55, null=True, blank=True)
    Director2countryOfIssue = models.CharField(max_length=55, null=True, blank=True)
    Director2passportExpiryDate = models.DateField(null=True, blank=True)
    Director2citizenship = models.CharField(max_length=55, null=True, blank=True)
    Director2specifiedCitizenship = models.CharField(max_length=55, null=True, blank=True)
    Director2countryOfResidence = models.CharField(max_length=55, null=True, blank=True)
    Director2preferredLanguage = models.CharField(max_length=55, null=True, blank=True)
    Director2NameOfEntity = models.CharField(max_length=55, null=True, blank=True)
    Director2tinNumber = models.CharField(max_length=55, null=True, blank=True)
    Director2taxResidency = models.CharField(max_length=55, null=True, blank=True)

    Director3FirstName = models.CharField(max_length=55, null=True, blank=True)
    Director3LastName = models.CharField(max_length=55, null=True, blank=True)
    Director3email = models.EmailField(null=True, blank=True)
    Director3contact = models.CharField(max_length=55, null=True, blank=True)
    Director3BirthDate = models.DateField(null=True, blank=True)
    Director3NationalID = models.CharField(max_length=55, null=True, blank=True)
    Director3passportIdNumber = models.CharField(max_length=55, null=True, blank=True)
    Director3countryOfIssue = models.CharField(max_length=55, null=True, blank=True)
    Director3passportExpiryDate = models.DateField(null=True, blank=True)
    Director3citizenship = models.CharField(max_length=55, null=True, blank=True)
    Director3specifiedCitizenship = models.CharField(max_length=55, null=True, blank=True)
    Director3countryOfResidence = models.CharField(max_length=55, null=True, blank=True)
    Director3preferredLanguage = models.CharField(max_length=55, null=True, blank=True)
    Director3NameOfEntity = models.CharField(max_length=55, null=True, blank=True)
    Director3tinNumber = models.CharField(max_length=55, null=True, blank=True)
    Director3taxResidency = models.CharField(max_length=55, null=True, blank=True)

    Director1isPep = models.CharField(max_length=55, null=True, blank=True)
    Director2isPep = models.CharField(max_length=55, null=True, blank=True)
    Director3isPep = models.CharField(max_length=55, null=True, blank=True)

    bankName = models.CharField(max_length=55, null=True, blank=True)
    Currency = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory1 = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory2 = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory3 = models.CharField(max_length=55, null=True, blank=True)
    groupASignatory4 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory1 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory2 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory3 = models.CharField(max_length=55, null=True, blank=True)
    groupBSignatory4 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser1 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser1AccessRights = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser2 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser2AccessRights = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser3 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser3AccessRights = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser4 = models.CharField(max_length=55, null=True, blank=True)
    authorizedUser4AccessRights = models.CharField(max_length=55, null=True, blank=True)
    modeOfOperation = models.CharField(max_length=55, null=True, blank=True)
    callBackProcessContact = models.CharField(max_length=55, null=True, blank=True)
    nameOfProposedOfficer = models.CharField(max_length=55, null=True, blank=True)

    registration_certificate_link = models.JSONField(blank=True, null=True)
    signature_link = models.JSONField(blank=True, null=True)
    bankStatement_link = models.JSONField(blank=True, null=True)
    professionalReference_link = models.JSONField(blank=True, null=True)
    national_id_link = models.JSONField(blank=True, null=True)
    passport_link = models.JSONField(blank=True, null=True)
    confirmationLetter_link = models.JSONField(blank=True, null=True)
    custody_accounts_link = models.JSONField(blank=True, null=True)
    source_of_funds_link = models.JSONField(blank=True, null=True)
    payslips_link = models.JSONField(blank=True, null=True)
    due_diligence_link = models.JSONField(blank=True, null=True)
    financial_statements_link = models.JSONField(blank=True, null=True)
    proof_of_ownership_link = models.JSONField(blank=True, null=True)
    lease_agreement_link = models.JSONField(blank=True, null=True)
    documentary_evidence_link = models.JSONField(blank=True, null=True)
    bank_statement_proceeds_link = models.JSONField(blank=True, null=True)
    bank_statement_link = models.JSONField(blank=True, null=True)
    cdd_documents_link = models.JSONField(blank=True, null=True)
    bank_statements_link = models.JSONField(blank=True, null=True)
    bank_statements_proceeds_link = models.JSONField(blank=True, null=True)
    notarised_documents_link = models.JSONField(blank=True, null=True)
    letter_from_donor_link = models.JSONField(blank=True, null=True)
    donor_source_of_wealth_link = models.JSONField(blank=True, null=True)
    donor_bank_statement_link = models.JSONField(blank=True, null=True)
    letter_from_relevant_org_link = models.JSONField(blank=True, null=True)
    lottery_bank_statement_link = models.JSONField(blank=True, null=True)
    creditor_agreement_link = models.JSONField(blank=True, null=True)
    creditor_cdd_link = models.JSONField(blank=True, null=True)
    creditor_bank_statement_link = models.JSONField(blank=True, null=True)
    legal_document_link = models.JSONField(blank=True, null=True)
    notary_letter_link = models.JSONField(blank=True, null=True)
    executor_letter_link = models.JSONField(blank=True, null=True)
    loan_agreement_link = models.JSONField(blank=True, null=True)
    loan_bank_statement_link = models.JSONField(blank=True, null=True)
    related_third_party_loan_agreement_link = models.JSONField(blank=True, null=True)
    related_third_party_cdd_link = models.JSONField(blank=True, null=True)
    related_third_party_bank_statement_link = models.JSONField(blank=True, null=True)
    unrelated_third_party_loan_agreement_link = models.JSONField(blank=True, null=True)
    unrelated_third_party_cdd_link = models.JSONField(blank=True, null=True)
    unrelated_third_party_bank_statement_link = models.JSONField(blank=True, null=True)
    signed_letter_from_notary_link = models.JSONField(blank=True, null=True)
    property_contract_link = models.JSONField(blank=True, null=True)
    insurance_pay_out_link = models.JSONField(blank=True, null=True)
    retirement_annuity_fund_statement_link = models.JSONField(blank=True, null=True)
    passport_link = models.JSONField(blank=True, null=True)
    utility_link = models.JSONField(blank=True, null=True)
    wealth_link = models.JSONField(blank=True, null=True)
    cv_link = models.JSONField(blank=True, null=True)
    funds_link = models.JSONField(blank=True, null=True)
    source_of_wealth_link = models.JSONField(blank=True, null=True)
    principals_identification_link = models.JSONField(blank=True, null=True)
    shareholders_link = models.JSONField(blank=True, null=True)
    declaration_of_trust_link = models.JSONField(blank=True, null=True)
    certificate_of_registration_link = models.JSONField(blank=True, null=True)
    deed_of_retirement_link = models.JSONField(blank=True, null=True)
    business_plan_link = models.JSONField(blank=True, null=True)
    registered_office_link = models.JSONField(blank=True, null=True)
    register_of_trustee_link = models.JSONField(blank=True, null=True)
    proof_of_source_of_funds_link = models.JSONField(blank=True, null=True)
    proof_of_source_of_wealth_link = models.JSONField(blank=True, null=True)
    latest_accounts_or_bank_statements_link = models.JSONField(blank=True, null=True)
    licence_link = models.JSONField(blank=True, null=True)
    certificate_of_incumbency_link = models.JSONField(blank=True, null=True)
    charter_link = models.JSONField(blank=True, null=True)
    latest_accounts_link = models.JSONField(blank=True, null=True)
    principals_foundation_link = models.JSONField(blank=True, null=True)
    financialForecast = models.JSONField(null=True, blank=True)
    other_necessary_documents_link = models.JSONField(null=True, blank=True)

    financialForecast = models.JSONField(null=True, blank=True)
    expectedAccountActivity = models.JSONField(null=True, blank=True)
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
    scheduler_email = models.EmailField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.EmailField(max_length=255, blank=True, null=True)
    client_id = models.IntegerField(blank=True, null=True)
    setter_name = models.CharField(max_length=255, blank=True)
    setter_email = models.EmailField(blank=True)
    action_taker_name = models.CharField(max_length=255, blank=True)
    action_taker_email = models.EmailField(blank=True)

    # Relationships
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_alerts', blank=True, null=True)

    # New fields to track reminder emails
    reminder_email_count = models.IntegerField(default=0)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    
class Reports(models.Model):
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    reporter_id = models.IntegerField()
    reporter_email = models.EmailField()
    reporter_name = models.CharField(max_length=255)
    client_reportee_id = models.IntegerField(blank=True, null=True)
    client_reportee_email = models.EmailField(blank=True, null=True)
    client_reportee_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report_link = models.URLField(blank=True, null=True)
    last_updated_by_id = models.IntegerField(blank=True, null=True)
    last_updated_by_name = models.CharField(max_length=255, blank=True, null=True)
    last_updated_by_email = models.EmailField(blank=True, null=True)


    def __str__(self):
        return self.title

class Reservation(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    fullName = models.CharField(max_length=255)
    clientContact = models.CharField(max_length=15)
    servicesToDiscuss = models.TextField()
    otherServices = models.TextField(blank=True, null=True)
    startTime = models.DateTimeField(blank=True, null=True, unique=True)
    endTime = models.DateTimeField(blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.startTime} - {self.endTime}"

class Options(models.Model):
    available_datetime = models.DateTimeField()
    day_of_week = models.CharField(max_length=10)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.available_datetime} - {self.status}"

class Request(models.Model):
    endpoint = models.CharField(max_length=100, null=True) # The url the user requested
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    response_code = models.PositiveSmallIntegerField() # Response status code
    method = models.CharField(max_length=10, null=True)  # Request method
    remote_address = models.CharField(max_length=20, null=True) # IP address of user
    exec_time = models.IntegerField(null=True) # Time taken to create the response
    date = models.DateTimeField(auto_now=True) # Date and time of request
    body_response = models.TextField() # Response data
    body_request = models.TextField() 

class WeeklyReport(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    report = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    public_date = models.DateTimeField(null=True, blank=True)
    reporter_name = models.CharField(max_length=255, blank=True, null=True)
    reporter_email = models.EmailField(blank=True, null=True)
    reporter_id = models.IntegerField(blank=True, null=True)
    report_table = models.JSONField(blank=True, null=True)
