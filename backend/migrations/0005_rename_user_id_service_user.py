# Generated by Django 4.2.7 on 2023-12-23 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_rename_user_service_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='user_id',
            new_name='user',
        ),
    ]
