# Generated by Django 5.0.2 on 2024-05-08 21:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0036_reports'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='NationalID',
            field=models.CharField(unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='passportIdNumber',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='UncompletedClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(blank=True, max_length=255, null=True)),
                ('lastName', models.CharField(blank=True, max_length=255, null=True)),
                ('taxResidency', models.CharField(blank=True, max_length=255, null=True)),
                ('tinNumber', models.CharField(blank=True, max_length=50, null=True)),
                ('citizenship', models.CharField(blank=True, max_length=50, null=True)),
                ('birthDate', models.DateField(blank=True, null=True)),
                ('countryOfResidence', models.CharField(blank=True, max_length=50, null=True)),
                ('passportIdNumber', models.CharField(max_length=50, unique=True)),
                ('countryOfIssue', models.CharField(blank=True, max_length=50, null=True)),
                ('passportExpiryDate', models.DateField(blank=True, null=True)),
                ('NameOfEntity', models.CharField(blank=True, max_length=100, null=True)),
                ('PrevNameOfEntity', models.CharField(blank=True, max_length=100, null=True)),
                ('TypeOfEntity', models.CharField(blank=True, max_length=100, null=True)),
                ('TypeOfLicense', models.CharField(blank=True, max_length=100, null=True)),
                ('sharePercent', models.CharField(blank=True, max_length=255, null=True)),
                ('currentAddress', models.CharField(blank=True, max_length=150)),
                ('clientContact', models.CharField(blank=True, max_length=20)),
                ('clientEmail', models.EmailField(max_length=254, unique=True)),
                ('preferredLanguage', models.CharField(blank=True, max_length=50)),
                ('registrarID', models.IntegerField(blank=True, null=True)),
                ('registrarEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('registrarFirstName', models.CharField(blank=True, max_length=255, null=True)),
                ('registrationDate', models.DateTimeField(auto_now_add=True)),
                ('isActive', models.BooleanField(blank=True, default=False, null=True)),
                ('activatorID', models.IntegerField(blank=True, null=True)),
                ('activatorEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('activatorFirstName', models.CharField(blank=True, max_length=255, null=True)),
                ('activationDate', models.DateField(blank=True, null=True)),
                ('deactivatorID', models.IntegerField(blank=True, null=True)),
                ('deactivatorEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('deactivatorFirstName', models.CharField(blank=True, max_length=255, null=True)),
                ('deactivationDate', models.DateField(blank=True, null=True)),
                ('designation', models.CharField(blank=True, max_length=255, null=True)),
                ('NationalID', models.CharField(max_length=255, unique=True)),
                ('introducerName', models.CharField(blank=True, max_length=255, null=True)),
                ('introducerEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('contactPersonName', models.CharField(blank=True, max_length=255, null=True)),
                ('contactPersonEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('contactPersonPhone', models.CharField(blank=True, max_length=20, null=True)),
                ('authorisedName', models.CharField(blank=True, max_length=255, null=True)),
                ('authorisedEmail', models.EmailField(blank=True, max_length=254, null=True)),
                ('authorisedPersonContact', models.CharField(blank=True, max_length=20, null=True)),
                ('authorisedCurrentAddress', models.CharField(blank=True, max_length=255, null=True)),
                ('authorisedRelationship', models.CharField(blank=True, max_length=255, null=True)),
                ('isPep', models.CharField(blank=True, max_length=5, null=True)),
                ('registration_certificate_link', models.URLField(blank=True, null=True)),
                ('national_id_link', models.URLField(blank=True, null=True)),
                ('incorporationDate', models.DateField(blank=True, null=True)),
                ('countryOfIncorporation', models.CharField(blank=True, max_length=50, null=True)),
                ('registeredOfficeAddress', models.CharField(blank=True, max_length=255, null=True)),
                ('businessActivity', models.CharField(blank=True, max_length=255, null=True)),
                ('countryOfOperation', models.CharField(blank=True, max_length=50, null=True)),
                ('changeName', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsName', models.CharField(blank=True, max_length=55, null=True)),
                ('financialServicesBusiness', models.CharField(blank=True, max_length=55, null=True)),
                ('jurisdictionName', models.CharField(blank=True, max_length=55, null=True)),
                ('jurisdictionAddress', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplication', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsPartner', models.CharField(blank=True, max_length=55, null=True)),
                ('criticised', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsJurisdictions', models.CharField(blank=True, max_length=55, null=True)),
                ('bankruptcyApplication', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsForfeit', models.CharField(blank=True, max_length=55, null=True)),
                ('receiverAppointed', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsReceiver', models.CharField(blank=True, max_length=55, null=True)),
                ('civilProceedings', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsFinancial', models.CharField(blank=True, max_length=55, null=True)),
                ('convicted', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsOffence', models.CharField(blank=True, max_length=55, null=True)),
                ('directorConvicted', models.CharField(blank=True, max_length=55, null=True)),
                ('similarApplicationDetailsDirector', models.CharField(blank=True, max_length=55, null=True)),
                ('RemittingParty', models.CharField(blank=True, max_length=55, null=True)),
                ('ModeOfPayment', models.CharField(blank=True, max_length=55, null=True)),
                ('RelationshipWithApplicant', models.CharField(blank=True, max_length=55, null=True)),
                ('ProposedNameOption1', models.CharField(blank=True, max_length=55, null=True)),
                ('ProposedNameOption2', models.CharField(blank=True, max_length=55, null=True)),
                ('ProposedNameOption3', models.CharField(blank=True, max_length=55, null=True)),
                ('proposedActivity', models.CharField(blank=True, max_length=55, null=True)),
                ('targetSectors', models.CharField(blank=True, max_length=55, null=True)),
                ('targetedCountries', models.CharField(blank=True, max_length=55, null=True)),
                ('specialLicense', models.CharField(blank=True, max_length=55, null=True)),
                ('secretary', models.CharField(blank=True, max_length=55, null=True)),
                ('productService', models.CharField(blank=True, max_length=55, null=True)),
                ('businessAddress', models.CharField(blank=True, max_length=55, null=True)),
                ('sourceOfFunds', models.CharField(blank=True, max_length=155, null=True)),
                ('otherSourceOfFunds', models.CharField(blank=True, max_length=55, null=True)),
                ('countrySourceFunds', models.CharField(blank=True, max_length=55, null=True)),
                ('netAnnualIncome', models.CharField(blank=True, max_length=55, null=True)),
                ('estimatedNetWorth', models.CharField(blank=True, max_length=55, null=True)),
                ('sourceOfWealth', models.CharField(blank=True, max_length=155, null=True)),
                ('otherSourceOfWealth', models.CharField(blank=True, max_length=55, null=True)),
                ('countrySourceWealth', models.CharField(blank=True, max_length=55, null=True)),
                ('bankInvolvedWealth', models.CharField(blank=True, max_length=55, null=True)),
                ('isMlDirectors', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1FirstName', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1LastName', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1email', models.EmailField(blank=True, max_length=254, null=True)),
                ('Director1contact', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1BirthDate', models.DateField(blank=True, null=True)),
                ('Director1NationalID', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1passportIdNumber', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1countryOfIssue', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1passportExpiryDate', models.DateField(blank=True, null=True)),
                ('Director1citizenship', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1specifiedCitizenship', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1countryOfResidence', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1preferredLanguage', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1NameOfEntity', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1tinNumber', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1taxResidency', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2FirstName', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2LastName', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2email', models.EmailField(blank=True, max_length=254, null=True)),
                ('Director2contact', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2BirthDate', models.DateField(blank=True, null=True)),
                ('Director2NationalID', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2passportIdNumber', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2countryOfIssue', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2passportExpiryDate', models.DateField(blank=True, null=True)),
                ('Director2citizenship', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2specifiedCitizenship', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2countryOfResidence', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2preferredLanguage', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2NameOfEntity', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2tinNumber', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2taxResidency', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3FirstName', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3LastName', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3email', models.EmailField(blank=True, max_length=254, null=True)),
                ('Director3contact', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3BirthDate', models.DateField(blank=True, null=True)),
                ('Director3NationalID', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3passportIdNumber', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3countryOfIssue', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3passportExpiryDate', models.DateField(blank=True, null=True)),
                ('Director3citizenship', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3specifiedCitizenship', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3countryOfResidence', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3preferredLanguage', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3NameOfEntity', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3tinNumber', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3taxResidency', models.CharField(blank=True, max_length=55, null=True)),
                ('Director1isPep', models.CharField(blank=True, max_length=55, null=True)),
                ('Director2isPep', models.CharField(blank=True, max_length=55, null=True)),
                ('Director3isPep', models.CharField(blank=True, max_length=55, null=True)),
                ('bankName', models.CharField(blank=True, max_length=55, null=True)),
                ('Currency', models.CharField(blank=True, max_length=55, null=True)),
                ('groupASignatory1', models.CharField(blank=True, max_length=55, null=True)),
                ('groupASignatory2', models.CharField(blank=True, max_length=55, null=True)),
                ('groupASignatory3', models.CharField(blank=True, max_length=55, null=True)),
                ('groupASignatory4', models.CharField(blank=True, max_length=55, null=True)),
                ('groupBSignatory1', models.CharField(blank=True, max_length=55, null=True)),
                ('groupBSignatory2', models.CharField(blank=True, max_length=55, null=True)),
                ('groupBSignatory3', models.CharField(blank=True, max_length=55, null=True)),
                ('groupBSignatory4', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser1', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser1AccessRights', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser2', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser2AccessRights', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser3', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser3AccessRights', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser4', models.CharField(blank=True, max_length=55, null=True)),
                ('authorizedUser4AccessRights', models.CharField(blank=True, max_length=55, null=True)),
                ('modeOfOperation', models.CharField(blank=True, max_length=55, null=True)),
                ('callBackProcessContact', models.CharField(blank=True, max_length=55, null=True)),
                ('nameOfProposedOfficer', models.CharField(blank=True, max_length=55, null=True)),
                ('signature_link', models.URLField(blank=True, null=True)),
                ('bankStatement_link', models.URLField(blank=True, null=True)),
                ('professionalReference_link', models.URLField(blank=True, null=True)),
                ('confirmationLetter_link', models.URLField(blank=True, null=True)),
                ('custody_accounts_link', models.URLField(blank=True, null=True)),
                ('source_of_funds_link', models.URLField(blank=True, null=True)),
                ('payslips_link', models.URLField(blank=True, null=True)),
                ('due_diligence_link', models.URLField(blank=True, null=True)),
                ('financial_statements_link', models.URLField(blank=True, null=True)),
                ('proof_of_ownership_link', models.URLField(blank=True, null=True)),
                ('lease_agreement_link', models.URLField(blank=True, null=True)),
                ('documentary_evidence_link', models.URLField(blank=True, null=True)),
                ('bank_statement_proceeds_link', models.URLField(blank=True, null=True)),
                ('bank_statement_link', models.URLField(blank=True, null=True)),
                ('cdd_documents_link', models.URLField(blank=True, null=True)),
                ('bank_statements_link', models.URLField(blank=True, null=True)),
                ('bank_statements_proceeds_link', models.URLField(blank=True, null=True)),
                ('notarised_documents_link', models.URLField(blank=True, null=True)),
                ('letter_from_donor_link', models.URLField(blank=True, null=True)),
                ('donor_source_of_wealth_link', models.URLField(blank=True, null=True)),
                ('donor_bank_statement_link', models.URLField(blank=True, null=True)),
                ('letter_from_relevant_org_link', models.URLField(blank=True, null=True)),
                ('lottery_bank_statement_link', models.URLField(blank=True, null=True)),
                ('creditor_agreement_link', models.URLField(blank=True, null=True)),
                ('creditor_cdd_link', models.URLField(blank=True, null=True)),
                ('creditor_bank_statement_link', models.URLField(blank=True, null=True)),
                ('legal_document_link', models.URLField(blank=True, null=True)),
                ('notary_letter_link', models.URLField(blank=True, null=True)),
                ('executor_letter_link', models.URLField(blank=True, null=True)),
                ('loan_agreement_link', models.URLField(blank=True, null=True)),
                ('loan_bank_statement_link', models.URLField(blank=True, null=True)),
                ('related_third_party_loan_agreement_link', models.URLField(blank=True, null=True)),
                ('related_third_party_cdd_link', models.URLField(blank=True, null=True)),
                ('related_third_party_bank_statement_link', models.URLField(blank=True, null=True)),
                ('unrelated_third_party_loan_agreement_link', models.URLField(blank=True, null=True)),
                ('unrelated_third_party_cdd_link', models.URLField(blank=True, null=True)),
                ('unrelated_third_party_bank_statement_link', models.URLField(blank=True, null=True)),
                ('signed_letter_from_notary_link', models.URLField(blank=True, null=True)),
                ('property_contract_link', models.URLField(blank=True, null=True)),
                ('insurance_pay_out_link', models.URLField(blank=True, null=True)),
                ('retirement_annuity_fund_statement_link', models.URLField(blank=True, null=True)),
                ('passport_link', models.URLField(blank=True, null=True)),
                ('utility_link', models.URLField(blank=True, null=True)),
                ('wealth_link', models.URLField(blank=True, null=True)),
                ('cv_link', models.URLField(blank=True, null=True)),
                ('funds_link', models.URLField(blank=True, null=True)),
                ('source_of_wealth_link', models.URLField(blank=True, null=True)),
                ('principals_identification_link', models.URLField(blank=True, null=True)),
                ('shareholders_link', models.URLField(blank=True, null=True)),
                ('declaration_of_trust_link', models.URLField(blank=True, null=True)),
                ('certificate_of_registration_link', models.URLField(blank=True, null=True)),
                ('deed_of_retirement_link', models.URLField(blank=True, null=True)),
                ('business_plan_link', models.URLField(blank=True, null=True)),
                ('registered_office_link', models.URLField(blank=True, null=True)),
                ('register_of_trustee_link', models.URLField(blank=True, null=True)),
                ('proof_of_source_of_funds_link', models.URLField(blank=True, null=True)),
                ('proof_of_source_of_wealth_link', models.URLField(blank=True, null=True)),
                ('latest_accounts_or_bank_statements_link', models.URLField(blank=True, null=True)),
                ('licence_link', models.URLField(blank=True, null=True)),
                ('certificate_of_incumbency_link', models.URLField(blank=True, null=True)),
                ('charter_link', models.URLField(blank=True, null=True)),
                ('latest_accounts_link', models.URLField(blank=True, null=True)),
                ('principals_foundation_link', models.URLField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]