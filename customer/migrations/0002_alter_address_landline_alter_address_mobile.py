# Generated by Django 5.1.7 on 2025-04-30 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='landline',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='mobile',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
