# Generated by Django 4.2.7 on 2023-12-21 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_remove_customuser_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='Address',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='LastName',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='accessLevel',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
