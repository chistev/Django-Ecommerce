# Generated by Django 4.2.7 on 2024-04-23 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0033_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
