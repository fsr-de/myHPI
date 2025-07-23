from django.db import migrations, models
import django.db.models.deletion


def fix_null_locales(apps, schema_editor):
    Locale = apps.get_model("wagtailcore", "Locale")
    default_locale = Locale.objects.first()
    MajorityVoteChoice = apps.get_model("polls", "MajorityVoteChoice")
    RankedChoiceOption = apps.get_model("polls", "RankedChoiceOption")
    MajorityVoteChoice.objects.filter(locale__isnull=True).update(locale=default_locale)
    RankedChoiceOption.objects.filter(locale__isnull=True).update(locale=default_locale)


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0013_assign_translation_keys"),
    ]
    operations = [
        migrations.AlterField(
            model_name="majorityvotechoice",
            name="translation_key",
            field=models.UUIDField(null=False, editable=False),
        ),
        migrations.AlterField(
            model_name="majorityvotechoice",
            name="locale",
            field=models.ForeignKey(
                null=False,
                editable=False,
                to="wagtailcore.locale",
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
        migrations.AlterField(
            model_name="rankedchoiceoption",
            name="translation_key",
            field=models.UUIDField(null=False, editable=False),
        ),
        migrations.AlterField(
            model_name="rankedchoiceoption",
            name="locale",
            field=models.ForeignKey(
                null=False,
                editable=False,
                to="wagtailcore.locale",
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="majorityvotechoice",
            unique_together={("translation_key", "locale")},
        ),
        migrations.AlterUniqueTogether(
            name="rankedchoiceoption",
            unique_together={("translation_key", "locale")},
        ),
        migrations.RunPython(fix_null_locales, reverse_code=migrations.RunPython.noop),
    ]
