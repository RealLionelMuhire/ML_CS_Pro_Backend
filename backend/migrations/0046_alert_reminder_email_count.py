# Generated by Django 4.2.13 on 2024-06-17 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0045_request_delete_requestlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="alert",
            name="reminder_email_count",
            field=models.IntegerField(default=0),
        ),
    ]
