# Generated by Django 3.1.8 on 2022-05-01 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_auto_20211125_1225"),
    ]

    operations = [
        migrations.AddField(
            model_name="informationpage",
            name="is_public",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="minutes",
            name="is_public",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="minuteslist",
            name="is_public",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
