# Generated by Django 5.1.7 on 2025-05-01 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_alter_address_landline_alter_address_mobile'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together={('first_name', 'last_name')},
        ),
    ]
