# Generated by Django 3.2.7 on 2021-11-17 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20211116_1928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='admin_addr',
        ),
    ]
