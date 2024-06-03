# Generated by Django 5.0.2 on 2024-05-03 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0035_customuser_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('reporter_id', models.IntegerField()),
                ('reporter_email', models.EmailField(max_length=254)),
                ('reporter_name', models.CharField(max_length=255)),
                ('client_reportee_id', models.IntegerField()),
                ('client_reportee_email', models.EmailField(max_length=254)),
                ('client_reportee_name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_link', models.URLField()),
            ],
        ),
    ]