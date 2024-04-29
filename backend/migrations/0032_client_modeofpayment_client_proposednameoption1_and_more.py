# Generated by Django 5.0.2 on 2024-04-18 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0031_remove_client_modeofpayment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='ModeOfPayment',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='ProposedNameOption1',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='ProposedNameOption2',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='ProposedNameOption3',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='RelationshipWithApplicant',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='RemittingParty',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='authorisedCurrentAddress',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='authorisedEmail',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='authorisedName',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='authorisedPersonContact',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='authorisedRelationship',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='bankInvolvedWealth',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='bankStatement_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='bankruptcyApplication',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='businessActivity',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='businessAddress',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='changeName',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='civilProceedings',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='contactPersonEmail',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='contactPersonName',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='contactPersonPhone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='convicted',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='countryOfIncorporation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='countryOfOperation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='countrySourceFunds',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='countrySourceWealth',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='criticised',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='directorConvicted',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='estimatedNetWorth',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='financialServicesBusiness',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='incorporationDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='isPep',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='jurisdictionAddress',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='jurisdictionName',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='national_id_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='netAnnualIncome',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='otherSourceOfFunds',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='otherSourceOfWealth',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='passport_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='productService',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='professionalReference_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='proposedActivity',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='receiverAppointed',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='registeredOfficeAddress',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='registration_certificate_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='secretary',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='signature_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplication',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsDirector',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsFinancial',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsForfeit',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsJurisdictions',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsName',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsOffence',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsPartner',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='similarApplicationDetailsReceiver',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='sourceOfFunds',
            field=models.CharField(blank=True, max_length=155, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='sourceOfWealth',
            field=models.CharField(blank=True, max_length=155, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='specialLicense',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='targetSectors',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='targetedCountries',
            field=models.CharField(blank=True, max_length=55, null=True),
        ),
    ]