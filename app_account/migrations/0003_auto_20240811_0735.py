# Generated by Django 3.2.24 on 2024-08-11 07:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_account', '0002_auto_20240702_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 10, 7, 35, 36, 437438)),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='code',
            field=models.CharField(default=145309, max_length=6),
        ),
        migrations.AlterField(
            model_name='verificationcode',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 8, 12, 7, 35, 36, 438150)),
        ),
    ]
