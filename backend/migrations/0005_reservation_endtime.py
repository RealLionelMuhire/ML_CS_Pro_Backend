# Generated by Django 5.0.2 on 2024-02-15 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_remove_reservation_endtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='endTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
