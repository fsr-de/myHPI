from django.core.management.base import BaseCommand

from myhpi.core.models import (
    FooterBase,
    FooterCategory,
    InformationPage,
    RedirectMenuItem,
    RootPage,
)


class Command(BaseCommand):
    help = "Initializes the site structure (e.g. creates the default footer)"
    root_page = None

    def handle(self, *args, **options):
        self.root_page = RootPage.objects.all().first()
        if self.root_page is None:
            return
        self._add_footer()

    def _add_footer(self):
        footer = FooterBase(title="Footer", is_public=True, depth=2)
        self.root_page.add_child(instance=footer)
        footer.save()

        footer_categories = [
            (
                FooterCategory(title="Fachschaft", is_public=True),
                [
                    RedirectMenuItem(
                        title="Twitter",
                        redirect_url="https://twitter.com/fachschaftsrat",
                        is_public=True,
                    ),
                    RedirectMenuItem(
                        title="Discord", redirect_url="https://discord.com", is_public=False
                    ),
                    RedirectMenuItem(
                        title="Telegram",
                        redirect_url="https://telegram.org",
                        is_public=False,
                    ),
                ],
            ),
            (
                FooterCategory(title="Rechtliches", is_public=True),
                [
                    InformationPage(
                        title="Impressum",
                        body="Test",
                        is_public=True,
                        author_visible=False,
                        show_in_menus=True,
                    ),
                    InformationPage(
                        title="Datenschutzerklärung",
                        body="Test",
                        is_public=True,
                        author_visible=False,
                        show_in_menus=True,
                    ),
                ],
            ),
            (
                FooterCategory(title="Entwicklung", is_public=True),
                [
                    RedirectMenuItem(
                        title="GitHub",
                        redirect_url="https://github.com/fsr-de/myHPI/",
                        is_public=True,
                    ),
                ],
            ),
            (FooterCategory(title="Sprache", is_public=True), []),
        ]

        for category, items in footer_categories:
            footer.add_child(instance=category)
            category.save()

            for item in items:
                category.add_child(instance=item)
                item.save()
