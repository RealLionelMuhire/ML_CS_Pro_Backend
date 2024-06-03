# Generated by Django 5.0.2 on 2024-05-21 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0041_alter_uncompletedclient_clientemail"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="expectedAccountActivity",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="client",
            name="financialForecast",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="uncompletedclient",
            name="expectedAccountActivity",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="uncompletedclient",
            name="financialForecast",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="uncompletedclient",
            name="clientEmail",
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]