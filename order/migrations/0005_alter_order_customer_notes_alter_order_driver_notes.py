# Generated by Django 5.1.7 on 2025-05-01 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_exchangerate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer_notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='order',
            name='driver_notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
