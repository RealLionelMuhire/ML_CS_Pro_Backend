# Generated by Django 5.0.2 on 2024-03-05 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0017_alter_client_registrarid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='registrarID',
            field=models.CharField(default=202, max_length=25),
            preserve_default=False,
        ),
    ]
