# Generated by Django 4.2.7 on 2024-01-21 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_personaldetails_security_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personaldetails',
            name='security_code',
        ),
    ]
