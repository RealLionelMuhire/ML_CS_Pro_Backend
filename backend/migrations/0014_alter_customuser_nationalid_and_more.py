# Generated by Django 5.0.2 on 2024-03-05 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_alter_customuser_isactive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='NationalID',
            field=models.CharField(max_length=35, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='UserRoles',
            field=models.CharField(max_length=40),
        ),
    ]
