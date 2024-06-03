# Generated by Django 5.0.2 on 2024-06-03 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0042_client_expectedaccountactivity_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="CathegoryOfEntity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="OtherSectorOfEntity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="SPVType",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="SectorOfEntity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="uncompletedclient",
            name="CathegoryOfEntity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="uncompletedclient",
            name="OtherSectorOfEntity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="uncompletedclient",
            name="SPVType",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="uncompletedclient",
            name="SectorOfEntity",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]