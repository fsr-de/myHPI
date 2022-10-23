from django.core.management.base import BaseCommand

from myhpi.core.models import Footer


class Command(BaseCommand):
    help = "Initializes the website (e.g. creates the default footer)"

    def handle(self, *args, **options):
        self._add_footer()

    def _add_footer(self):
        footer = Footer()
        footer.column_1 = "# Fachschaft\r\n\r\n- [Twitter](https://twitter.com/fachschaftsrat)\r\n- [Discord](https://discord.com)\r\n- [Telegram](https://telegram.org)"
        footer.column_2 = "# Rechtliches\r\n\r\n- [Impressum]()\r\n- [Datenschutzerklärung]()"
        footer.column_3 = "# Entwicklung\r\n\r\n- [GitHub](https://github.com/fsr-de/myHPI/)"
        footer.column_4 = "# Sprache\r\n\r\n"
        footer.save()
