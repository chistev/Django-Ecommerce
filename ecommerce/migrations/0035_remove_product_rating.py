# Generated by Django 4.2.7 on 2024-04-25 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0034_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='rating',
        ),
    ]
