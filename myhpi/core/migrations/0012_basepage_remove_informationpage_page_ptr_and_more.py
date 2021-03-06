# Generated by Django 4.0.4 on 2022-06-07 07:30

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("wagtailcore", "0066_collection_management_permissions"),
        ("core", "0011_auto_20220501_1642"),
    ]

    operations = [
        migrations.CreateModel(
            name="BasePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("is_public", models.BooleanField()),
                (
                    "visible_for",
                    modelcluster.fields.ParentalManyToManyField(
                        related_name="visible_basepages", to="auth.group"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.DeleteModel(
            name="FirstLevelMenuItem",
        ),
        migrations.DeleteModel(
            name="InformationPage",
        ),
        migrations.DeleteModel(
            name="Minutes",
        ),
        migrations.DeleteModel(
            name="MinutesList",
        ),
        migrations.DeleteModel(
            name="RootPage",
        ),
        migrations.DeleteModel(
            name="SecondLevelMenuItem",
        ),
        migrations.DeleteModel(
            name="TaggedMinutes",
        ),
    ]
