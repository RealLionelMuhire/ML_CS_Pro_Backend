# Generated by Django 4.2.13 on 2024-06-22 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0050_alter_reports_client_reportee_email_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reports",
            name="report_link",
            field=models.URLField(blank=True, null=True),
        ),
    ]
