# Generated by Django 5.1.7 on 2025-05-09 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0012_customer_residence_ehden_customer_residence_zgharta'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='residence_ehden',
            new_name='residenceEhden',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='residence_zgharta',
            new_name='residenceZgharta',
        ),
    ]
