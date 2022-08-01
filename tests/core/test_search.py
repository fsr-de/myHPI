from django.test import Client, TestCase

from tests.core.setup import setup_data


class SearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_data = setup_data()

    def sign_in_as_student(self):
        student = self.test_data["users"][1]
        self.client.force_login(student)

    def sign_in_as_student_representative(self):
        student_representative = self.test_data["users"][2]
        self.client.force_login(student_representative)

    def test_search_page_exists(self):
        search_page = self.client.get("/en/search/", follow=True)
        self.assertEqual(search_page.status_code, 200)

    def test_can_find_public_page(self):
        search_page = self.client.get("/en/search/", data={"query": "Page"}, follow=True)
        self.assertInHTML("Public Page", search_page.rendered_content)

    def test_unauthorized_user_can_not_find_pages(self):
        search_page = self.client.get("/en/search/", data={"query": "Page"}, follow=True)
        self.assertNotIn("Common Page", search_page.rendered_content)
        self.assertNotIn("Private Page", search_page.rendered_content)

    def test_user_in_group_can_find_group_restricted_pages(self):
        self.sign_in_as_student()
        search_page = self.client.get("/en/search/", data={"query": "Page"}, follow=True)
        self.assertInHTML("Public Page", search_page.rendered_content)
        self.assertInHTML("Common Page", search_page.rendered_content)

    def test_user_can_not_find_pages_only_for_other_groups(self):
        self.sign_in_as_student()
        search_page = self.client.get("/en/search/", data={"query": "Page"}, follow=True)
        self.assertNotIn("Private Page", search_page.rendered_content)

    def test_user_in_group_can_find_multiple_group_restricted_pages(self):
        self.sign_in_as_student_representative()
        search_page = self.client.get("/en/search/", data={"query": "Page"}, follow=True)
        self.assertInHTML("Public Page", search_page.rendered_content)
        self.assertInHTML("Common Page", search_page.rendered_content)
        self.assertInHTML("Private Page", search_page.rendered_content)
