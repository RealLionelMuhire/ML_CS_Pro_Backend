# Generated by Django 4.2.7 on 2023-12-23 15:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_rename_user_id_service_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
