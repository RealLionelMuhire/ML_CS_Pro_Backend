# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField('BackendCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class BackendAlert(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    action_taken = models.IntegerField()
    schedule_date = models.DateTimeField()
    set_date = models.DateTimeField()
    action_taken_date = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateTimeField()
    scheduler_name = models.CharField(max_length=255)
    scheduler_email = models.CharField(max_length=254)
    client_name = models.CharField(max_length=255)
    client_email = models.CharField(max_length=254)
    client_id = models.IntegerField(blank=True, null=True)
    setter_name = models.CharField(max_length=255)
    setter_email = models.CharField(max_length=254)
    action_taker_name = models.CharField(max_length=255)
    action_taker_email = models.CharField(max_length=254)
    user = models.ForeignKey('BackendCustomuser', models.DO_NOTHING, blank=True, null=True)
    is_active = models.IntegerField()
    action_taken_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'backend_alert'


class BackendClient(models.Model):
    id = models.BigAutoField(primary_key=True)
    firstname = models.CharField(db_column='firstName', max_length=255)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=255)  # Field name made lowercase.
    tinnumber = models.CharField(db_column='tinNumber', max_length=50)  # Field name made lowercase.
    citizenship = models.CharField(max_length=50)
    birthdate = models.DateField(db_column='birthDate', blank=True, null=True)  # Field name made lowercase.
    passportidnumber = models.CharField(db_column='passportIdNumber', unique=True, max_length=50)  # Field name made lowercase.
    countryofissue = models.CharField(db_column='countryOfIssue', max_length=50, blank=True, null=True)  # Field name made lowercase.
    passportexpirydate = models.DateField(db_column='passportExpiryDate', blank=True, null=True)  # Field name made lowercase.
    clientcontact = models.CharField(db_column='clientContact', max_length=20)  # Field name made lowercase.
    clientemail = models.CharField(db_column='clientEmail', unique=True, max_length=254)  # Field name made lowercase.
    preferredlanguage = models.CharField(db_column='preferredLanguage', max_length=50)  # Field name made lowercase.
    user = models.ForeignKey('BackendCustomuser', models.DO_NOTHING)
    taxresidency = models.CharField(db_column='taxResidency', max_length=255)  # Field name made lowercase.
    activatoremail = models.CharField(db_column='activatorEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    activatorfirstname = models.CharField(db_column='activatorFirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    activatorid = models.IntegerField(db_column='activatorID', blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    registrarfirstname = models.CharField(db_column='registrarFirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    registraremail = models.CharField(db_column='registrarEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    registrarid = models.IntegerField(db_column='registrarID', blank=True, null=True)  # Field name made lowercase.
    deactivatoremail = models.CharField(db_column='deactivatorEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    deactivatorfirstname = models.CharField(db_column='deactivatorFirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    deactivatorid = models.IntegerField(db_column='deactivatorID', blank=True, null=True)  # Field name made lowercase.
    contactpersonname = models.CharField(db_column='contactPersonName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nameofentity = models.CharField(db_column='NameOfEntity', max_length=100, blank=True, null=True)  # Field name made lowercase.
    currentaddress = models.CharField(db_column='currentAddress', max_length=150)  # Field name made lowercase.
    activationdate = models.DateField(db_column='activationDate', blank=True, null=True)  # Field name made lowercase.
    deactivationdate = models.DateField(db_column='deactivationDate', blank=True, null=True)  # Field name made lowercase.
    registrationdate = models.DateTimeField(db_column='registrationDate')  # Field name made lowercase.
    contactpersonemail = models.CharField(db_column='contactPersonEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    contactpersonphone = models.CharField(db_column='contactPersonPhone', max_length=20, blank=True, null=True)  # Field name made lowercase.
    designation = models.CharField(max_length=255, blank=True, null=True)
    introduceremail = models.CharField(db_column='introducerEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    introducername = models.CharField(db_column='introducerName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    sharepercent = models.CharField(db_column='sharePercent', max_length=255, blank=True, null=True)  # Field name made lowercase.
    bankstatement_link = models.CharField(db_column='bankStatement_link', max_length=200, blank=True, null=True)  # Field name made lowercase.
    professionalreference_link = models.CharField(db_column='professionalReference_link', max_length=200, blank=True, null=True)  # Field name made lowercase.
    signature_link = models.CharField(max_length=200, blank=True, null=True)
    prevnameofentity = models.CharField(db_column='PrevNameOfEntity', max_length=100, blank=True, null=True)  # Field name made lowercase.
    typeofentity = models.CharField(db_column='TypeOfEntity', max_length=100, blank=True, null=True)  # Field name made lowercase.
    typeoflicense = models.CharField(db_column='TypeOfLicense', max_length=100, blank=True, null=True)  # Field name made lowercase.
    authorisedcurrentaddress = models.CharField(db_column='authorisedCurrentAddress', max_length=255, blank=True, null=True)  # Field name made lowercase.
    authorisedemail = models.CharField(db_column='authorisedEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    authorisedname = models.CharField(db_column='authorisedName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    authorisedpersoncontact = models.CharField(db_column='authorisedPersonContact', max_length=20, blank=True, null=True)  # Field name made lowercase.
    authorisedrelationship = models.CharField(db_column='authorisedRelationship', max_length=255, blank=True, null=True)  # Field name made lowercase.
    businessactivity = models.CharField(db_column='businessActivity', max_length=255, blank=True, null=True)  # Field name made lowercase.
    countryofincorporation = models.CharField(db_column='countryOfIncorporation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    countryofoperation = models.CharField(db_column='countryOfOperation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    countryofresidence = models.CharField(db_column='countryOfResidence', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ispep = models.CharField(db_column='isPep', max_length=5, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'backend_client'


class BackendCustomuser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    userroles = models.CharField(db_column='UserRoles', max_length=20)  # Field name made lowercase.
    email = models.CharField(unique=True, max_length=254)
    firstname = models.CharField(db_column='FirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nationalid = models.CharField(db_column='NationalID', unique=True, max_length=25)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=150)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    registrarfirstname = models.CharField(db_column='registrarFirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    registrarid = models.IntegerField(db_column='registrarID', blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    accesslevel = models.CharField(db_column='accessLevel', max_length=20, blank=True, null=True)  # Field name made lowercase.
    contact = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.DateField(db_column='BirthDate', blank=True, null=True)  # Field name made lowercase.
    activationdate = models.DateTimeField(db_column='activationDate', blank=True, null=True)  # Field name made lowercase.
    activatoremail = models.CharField(db_column='activatorEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    activatorfirstname = models.CharField(db_column='activatorFirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    activatorid = models.IntegerField(db_column='activatorID', blank=True, null=True)  # Field name made lowercase.
    deactivationdate = models.DateTimeField(db_column='deactivationDate', blank=True, null=True)  # Field name made lowercase.
    deactivatoremail = models.CharField(db_column='deactivatorEmail', max_length=254, blank=True, null=True)  # Field name made lowercase.
    deactivatorfirstname = models.CharField(db_column='deactivatorFirstName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    deactivatorid = models.IntegerField(db_column='deactivatorID', blank=True, null=True)  # Field name made lowercase.
    registrationdate = models.DateTimeField(db_column='registrationDate')  # Field name made lowercase.
    is_staff = models.IntegerField()
    username = models.CharField(max_length=255, blank=True, null=True)
    contract_link = models.CharField(max_length=200, blank=True, null=True)
    cv_link = models.CharField(max_length=200, blank=True, null=True)
    passport_link = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'backend_customuser'


class BackendCustomuserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(BackendCustomuser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'backend_customuser_groups'
        unique_together = (('customuser', 'group'),)


class BackendCustomuserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(BackendCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'backend_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class BackendEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'backend_event'


class BackendOptions(models.Model):
    id = models.BigAutoField(primary_key=True)
    available_datetime = models.DateTimeField()
    day_of_week = models.CharField(max_length=10)
    status = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'backend_options'


class BackendPasswordresettoken(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(unique=True, max_length=255)
    expiration_time = models.DateTimeField()
    user = models.ForeignKey(BackendCustomuser, models.DO_NOTHING)
    resetdate = models.DateTimeField(db_column='resetDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'backend_passwordresettoken'


class BackendReservation(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField()
    email = models.CharField(max_length=254)
    full_name = models.CharField(max_length=255)
    phone_contact = models.CharField(max_length=15)
    service_title = models.CharField(max_length=255)
    appointment_datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'backend_reservation'


class BackendService(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    objective = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.IntegerField()
    total_elapsed_time = models.DecimalField(max_digits=10, decimal_places=2)
    service_cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    provider_id = models.IntegerField(blank=True, null=True)
    provider_email = models.CharField(max_length=254, blank=True, null=True)
    provider_name = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    client_email = models.CharField(max_length=254, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    serviced_client_id = models.IntegerField(blank=True, null=True)
    initationdate = models.DateTimeField(db_column='initationDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'backend_service'


class BackendUseractionlog(models.Model):
    id = models.BigAutoField(primary_key=True)
    action_time = models.DateTimeField()
    action_type = models.CharField(max_length=20)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(BackendCustomuser, models.DO_NOTHING, blank=True, null=True)
    granted_by = models.ForeignKey(BackendCustomuser, models.DO_NOTHING, related_name='backenduseractionlog_granted_by_set', blank=True, null=True)
    granted_by_fullname = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'backend_useractionlog'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(BackendCustomuser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
