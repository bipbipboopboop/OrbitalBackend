# Generated by Django 4.0.5 on 2022-07-24 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_rename_user_order_customer_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='user',
            new_name='customer',
        ),
    ]
