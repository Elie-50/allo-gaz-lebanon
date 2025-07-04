# Generated by Django 5.1.7 on 2025-05-13 13:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0014_remove_customer_is_deleted_customer_isactive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='text',
        ),
        migrations.AddField(
            model_name='address',
            name='building',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='address',
            name='floor',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='address',
            name='region',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='address',
            name='street',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='phonenumber',
            name='mobile',
            field=models.CharField(default='', max_length=40, validators=[django.core.validators.RegexValidator(message='Enter a valid international phone number in E.164 format (e.g., +12345678901).', regex='^\\+[1-9]\\d{6,14}$')]),
        ),
    ]
