from wagtail.test.utils import WagtailPageTests

from myhpi.core.models import InformationPage, MenuItem, Minutes, MinutesList, RootPage


class PageCreationTests(WagtailPageTests):
    def test_can_create_a_menu_under_root_page(self):
        self.assertCanCreateAt(RootPage, MenuItem)

    def test_cant_create_a_menu_under_information_page(self):
        self.assertCanNotCreateAt(InformationPage, MenuItem)

    def test_can_create_a_information_page_under_menu(self):
        self.assertCanCreateAt(MenuItem, InformationPage)

    def test_cant_create_a_information_page_under_information_page(self):
        self.assertCanCreateAt(InformationPage, InformationPage)

    def test_can_create_a_minutes_list_under_root_page(self):
        self.assertCanCreateAt(RootPage, MinutesList)

    def test_can_create_a_minutes_list_under_menu(self):
        self.assertCanCreateAt(MenuItem, MinutesList)

    def test_can_only_create_minutes_under_minutes_pages(self):
        self.assertAllowedParentPageTypes(Minutes, {MinutesList})
