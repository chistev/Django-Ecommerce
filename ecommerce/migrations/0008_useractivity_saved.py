# Generated by Django 4.2.7 on 2024-03-05 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0007_useractivity_delete_viewedproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='saved',
            field=models.BooleanField(default=False),
        ),
    ]