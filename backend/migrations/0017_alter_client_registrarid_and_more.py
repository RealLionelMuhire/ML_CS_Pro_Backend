# Generated by Django 5.0.2 on 2024-03-05 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_alter_client_registraremail_alter_client_registrarid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='registrarID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='registrarID',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]