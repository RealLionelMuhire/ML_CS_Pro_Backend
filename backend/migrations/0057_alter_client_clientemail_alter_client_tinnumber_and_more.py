# Generated by Django 4.2.13 on 2024-09-17 23:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0056_auto_20240917_2323"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="clientEmail",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="client",
            name="tinNumber",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.CreateModel(
            name="WeeklyReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("report", models.TextField()),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("published", models.BooleanField(default=False)),
                ("public_date", models.DateTimeField(blank=True, null=True)),
                (
                    "reporter_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "reporter_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                ("reporter_id", models.IntegerField(blank=True, null=True)),
                ("report_table", models.JSONField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
