# Generated by Django 5.1.7 on 2025-05-07 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0004_rename_category_item_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='items'),
        ),
    ]
