# Generated by Django 4.0.7 on 2024-02-01 09:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0011_basepoll_rankedchoiceballot_rankedchoiceoption_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rankedchoiceballotentry',
            unique_together={('ballot', 'rank'), ('ballot', 'option')},
        ),
    ]
