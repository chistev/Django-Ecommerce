# Generated by Django 4.2.7 on 2024-04-09 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_city_options_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='personaldetails',
            name='security_code',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
    ]