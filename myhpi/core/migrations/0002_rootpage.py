from django.db import migrations

# Manual migration, based on:
# https://www.accordbox.com/blog/create-wagtail-project/#home
# https://github.com/wagtail/wagtail/tree/v2.11.3/wagtail/project_template/home/migrations


def create_homepage(apps, schema_editor):
    # Get models
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")
    Site = apps.get_model("wagtailcore.Site")
    RootPage = apps.get_model("core.RootPage")
    Footer = apps.get_model("core.Footer")

    # Delete the default homepage generated in 0002_initial_data of wagtailcore
    # If migration is run multiple times, it may have already been deleted
    Page.objects.filter(id=2).delete()

    # Create content type for homepage model
    homepage_content_type, __ = ContentType.objects.get_or_create(
        model="rootpage", app_label="core"
    )

    # Create content type for footer model
    footer_content_type, __ = ContentType.objects.get_or_create(model="footer", app_label="core")

    # Create a new homepage
    homepage, __ = RootPage.objects.get_or_create(
        title="Startseite",
        draft_title="myHPI",
        slug="home",
        content_type=homepage_content_type,
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
        is_public=True,
        author_visible=False,
        body="Willkommen auf myHPI.de!\n\nmyHPI ist eine Webseite von und für Studierende am Hasso-Plattner-Institut (HPI) in Potsdam und für diejenigen, die es noch werden wollen. Auf dieser Seite werden verschiedene Informationen rund um das Studium am HPI zur Verfügung gestellt. Der Fachschaftsrat Digital Engineering betreibt die Webseite und veröffentlicht hier unter anderem seine Sitzungsprotokolle.\n\nNicht alle Informationen sind öffentlich zugänglich, für einige Bereiche der Webseite ist ein HPI-Login notwendig.",
    )

    # Create a site with the new homepage set as the root
    Site.objects.get_or_create(
        hostname="localhost",
        root_page=homepage,
        is_default_site=True,
    )

    Footer.objects.get_or_create(
        column_1="# Fachschaft\r\n\r\n- [Twitter](https://twitter.com/fachschaftsrat)\r\n- [Discord](https://discord.com)\r\n- [Telegram](https://telegram.org)",
        column_2="# Rechtliches\r\n\r\n- [Impressum]()\r\n- [Datenschutzerklärung]()",
        column_3="# Entwicklung\r\n\r\n- [GitHub](https://github.com/fsr-de/myHPI/)",
        column_4="# Sprache\r\n\r\n",
    )


class Migration(migrations.Migration):
    run_before = [
        ("wagtailcore", "0053_locale_model"),
    ]

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_homepage),
    ]
