from django.db import migrations
import uuid


def assign_translation_keys(apps, schema_editor):
    MajorityVoteChoice = apps.get_model("polls", "MajorityVoteChoice")
    RankedChoiceOption = apps.get_model("polls", "RankedChoiceOption")
    Locale = apps.get_model("wagtailcore", "Locale")
    default_locale = Locale.objects.first()
    for obj in MajorityVoteChoice.objects.all():
        obj.translation_key = uuid.uuid4()
        obj.locale = default_locale
        obj.save(update_fields=["translation_key", "locale"])
    for obj in RankedChoiceOption.objects.all():
        obj.translation_key = uuid.uuid4()
        obj.locale = default_locale
        obj.save(update_fields=["translation_key", "locale"])


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0012_alter_majorityvotechoice_options_and_more"),
    ]
    operations = [
        migrations.RunPython(assign_translation_keys, reverse_code=migrations.RunPython.noop),
    ]
