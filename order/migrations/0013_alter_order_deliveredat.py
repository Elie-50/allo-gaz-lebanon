# Generated by Django 5.1.7 on 2025-05-21 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_alter_order_isactive_alter_order_money_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='deliveredAt',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
