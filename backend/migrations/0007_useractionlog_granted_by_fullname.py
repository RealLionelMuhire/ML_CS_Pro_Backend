# Generated by Django 4.2.7 on 2023-12-11 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_useractionlog_granted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractionlog',
            name='granted_by_fullname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
