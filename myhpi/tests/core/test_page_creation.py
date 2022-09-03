from wagtail.test.utils import WagtailPageTests

from myhpi.core.models import (
    FirstLevelMenuItem,
    InformationPage,
    Minutes,
    MinutesList,
    RootPage,
    SecondLevelMenuItem,
)


class PageCreationTests(WagtailPageTests):
    def test_can_create_a_first_level_menu_under_root_page(self):
        self.assertCanCreateAt(RootPage, FirstLevelMenuItem)

    def test_cant_create_a_first_level_menu_under_information_page(self):
        self.assertCanNotCreateAt(InformationPage, FirstLevelMenuItem)

    def test_can_create_a_second_level_menu_under_first_level_menu(self):
        self.assertCanCreateAt(FirstLevelMenuItem, SecondLevelMenuItem)

    def test_cant_create_a_second_level_menu_under_root_page(self):
        self.assertCanNotCreateAt(RootPage, SecondLevelMenuItem)

    def test_cant_create_a_second_level_menu_under_information_page(self):
        self.assertCanNotCreateAt(InformationPage, SecondLevelMenuItem)

    def test_can_create_a_information_page_under_first_level_menu(self):
        self.assertCanCreateAt(FirstLevelMenuItem, InformationPage)

    def test_can_create_a_information_page_under_second_level_menu(self):
        self.assertCanCreateAt(SecondLevelMenuItem, InformationPage)

    def test_cant_create_a_information_page_under_information_page(self):
        self.assertCanCreateAt(InformationPage, InformationPage)

    def test_can_create_a_minutes_list_under_root_page(self):
        self.assertCanCreateAt(RootPage, MinutesList)

    def test_can_create_a_minutes_list_under_first_level_menu(self):
        self.assertCanCreateAt(FirstLevelMenuItem, MinutesList)

    def test_can_create_a_minutes_list_under_second_level_menu(self):
        self.assertCanCreateAt(SecondLevelMenuItem, MinutesList)

    def test_can_only_create_minutes_under_minutes_pages(self):
        self.assertAllowedParentPageTypes(Minutes, {MinutesList})
