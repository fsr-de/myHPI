# Generated by Django 3.1.8 on 2021-06-12 10:31

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0002_auto_20210612_1217"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="end_date",
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="poll",
            name="start_date",
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
