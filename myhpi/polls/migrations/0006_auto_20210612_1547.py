# Generated by Django 3.1.8 on 2021-06-12 13:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0005_remove_pollchoice_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="poll",
            name="max_allowed_answers",
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name="poll",
            name="results_visible",
            field=models.BooleanField(default=False),
        ),
    ]
