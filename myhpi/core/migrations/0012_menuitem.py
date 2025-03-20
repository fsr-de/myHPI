# Generated by Django 4.2.9 on 2024-04-06 17:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_alter_taggedminutes_tag"),
    ]

    operations = [
        migrations.CreateModel(
            name="MenuItem",
            fields=[
                (
                    "basepage_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="core.basepage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("core.basepage",),
        ),
    ]
