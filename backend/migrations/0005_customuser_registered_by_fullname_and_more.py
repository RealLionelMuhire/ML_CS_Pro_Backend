# Generated by Django 4.2.7 on 2023-12-11 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_remove_customuser_registered_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='registered_by_fullname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='registered_by_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]