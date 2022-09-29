from myhpi.core.models import RedirectMenuItem, RootPage
from myhpi.tests.core.utils import MyHPIPageTestCase


class RedirectMenuItemTests(MyHPIPageTestCase):
    def create_redirect_menu_item(self, name, redirect_url):
        root_page = RootPage.objects.get(slug="myhpi")
        redirect_menu_item = RedirectMenuItem(
            title=name, redirect_url=redirect_url, slug=name, is_public=True
        )
        root_page.add_child(instance=redirect_menu_item)
        return redirect_menu_item

    def setUp(self):
        super().setUp()
        self.redirect_menu_item = self.create_redirect_menu_item("example", "https://example.com")

    def test_redirect_menu_item_redirects(self):
        print(RedirectMenuItem.objects.count())
        print(RedirectMenuItem.objects.get(slug="example"))
        redirection = self.client.get("/en/example/")
        self.assertEqual(redirection.status_code, 302)

    def test_redirect_menu_item_redirects_to_page(self):
        redirection = self.client.get("/en/example/", follow=True)
        self.assertEqual(redirection.redirect_chain[0][0], "https://example.com")
