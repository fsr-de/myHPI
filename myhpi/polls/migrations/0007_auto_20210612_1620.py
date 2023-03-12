# Generated by Django 3.1.8 on 2021-06-12 14:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("polls", "0006_auto_20210612_1547"),
    ]

    operations = [
        migrations.AlterField(
            model_name="poll",
            name="participants",
            field=models.ManyToManyField(related_name="polls", to=settings.AUTH_USER_MODEL),
        ),
    ]
