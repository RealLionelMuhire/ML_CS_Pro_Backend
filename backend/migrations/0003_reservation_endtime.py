# Generated by Django 5.0.2 on 2024-02-15 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_remove_reservation_endtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='endTime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
