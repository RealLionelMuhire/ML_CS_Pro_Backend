# Generated by Django 5.0.2 on 2024-03-05 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0008_rename_registrarfirstname_customuser_registrarname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='registrarName',
            field=models.CharField(default='Migrate Set', max_length=255),
            preserve_default=False,
        ),
    ]
