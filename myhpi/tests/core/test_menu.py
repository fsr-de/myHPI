from myhpi.tests.core.utils import MyHPIPageTestCase


def get_as_page_path_lookup(page_lookup):
    page_path_lookup = {}
    for page_path in page_lookup:
        page_path_lookup[page_path] = [child.path for child in page_lookup[page_path]]
    return page_path_lookup


class MenuTests(MyHPIPageTestCase):
    def test_root_page_in_context(self):
        start_page = self.client.get("/en", follow=True)
        self.assertEqual(self.root_page.path, start_page.context["root_page"].path)

    def test_page_lookup_is_correct_for_guests(self):
        start_page = self.client.get("/en", follow=True)
        lookup = get_as_page_path_lookup(start_page.context["pages_by_parent"])
        self.assertDictEqual(
            {
                self.root_page.path: [self.information_menu.path],
                self.information_menu.path: [self.public_page.path],
                self.public_page.path: [],
            },
            lookup,
        )

    def test_page_lookup_is_correct_for_students(self):
        self.sign_in_as_student()
        start_page = self.client.get("/en", follow=True)
        lookup = get_as_page_path_lookup(start_page.context["pages_by_parent"])
        self.maxDiff = None
        self.assertDictEqual(
            {
                self.root_page.path: [self.information_menu.path],
                self.information_menu.path: [self.common_page.path, self.public_page.path],
                self.public_page.path: [],
                self.common_page.path: [],
                self.student_representative_group_minutes.path: [],
            },
            lookup,
        )

    def test_page_lookup_is_correct_for_student_representatives(self):
        self.sign_in_as_student_representative()
        start_page = self.client.get("/en", follow=True)
        lookup = get_as_page_path_lookup(start_page.context["pages_by_parent"])
        self.maxDiff = None
        self.assertDictEqual(
            {
                self.root_page.path: [self.information_menu.path],
                self.information_menu.path: [
                    self.common_page.path,
                    self.private_page.path,
                    self.public_page.path,
                ],
                self.public_page.path: [],
                self.common_page.path: [],
                self.private_page.path: [],
                self.student_representative_group_minutes.path: [],
            },
            lookup,
        )
