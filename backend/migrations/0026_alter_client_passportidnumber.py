# Generated by Django 5.0.2 on 2024-04-07 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0025_customuser_preferredlanguage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='passportIdNumber',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]