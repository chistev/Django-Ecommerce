# Generated by Django 4.2.7 on 2024-04-17 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0025_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='super_category',
            field=models.CharField(choices=[('supermarket', 'Supermarket')], default='supermarket', max_length=20),
        ),
    ]
