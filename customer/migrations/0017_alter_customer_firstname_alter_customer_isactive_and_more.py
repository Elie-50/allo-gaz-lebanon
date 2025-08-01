# Generated by Django 5.1.7 on 2025-05-19 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0016_customer_residencekoura_customer_residencetripoli'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='firstName',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='customer',
            name='isActive',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='lastName',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='customer',
            name='middleName',
            field=models.CharField(db_index=True, max_length=50),
        ),
    ]
