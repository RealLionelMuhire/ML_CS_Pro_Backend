# Generated by Django 4.2.7 on 2023-11-23 08:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("backend", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="customuser",
            old_name="Email",
            new_name="email",
        ),
        migrations.RenameField(
            model_name="customuser",
            old_name="Username",
            new_name="username",
        ),
    ]
