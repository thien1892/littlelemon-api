# Generated by Django 4.2.4 on 2023-08-10 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0005_cart_price_cart_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='cart',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
