# Generated by Django 5.0.2 on 2024-03-25 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_alter_customuser_isactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='national_id_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
