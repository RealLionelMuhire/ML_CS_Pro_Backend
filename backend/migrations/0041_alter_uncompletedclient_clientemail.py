# Generated by Django 5.0.2 on 2024-05-21 22:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0040_remove_client_passportexpirydate_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uncompletedclient",
            name="clientEmail",
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]
