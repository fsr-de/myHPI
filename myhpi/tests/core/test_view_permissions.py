from myhpi.tests.core.utils import MyHPIPageTestCase


class ViewPermissionTests(MyHPIPageTestCase):
    def test_unauthorized_user_can_view_public_page(self):
        response = self.client.get(self.public_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_can_not_view_common_page(self):
        response = self.client.get(self.common_page.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_user_can_not_view_private_page(self):
        response = self.client.get(self.private_page.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_student_can_view_public_page(self):
        self.sign_in_as_student()
        response = self.client.get(self.public_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_student_can_view_common_page(self):
        self.sign_in_as_student()
        response = self.client.get(self.common_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_student_can_not_view_private_page(self):
        self.sign_in_as_student()
        response = self.client.get(self.private_page.url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_student_representative_can_view_public_page(self):
        self.sign_in_as_student_representative()
        response = self.client.get(self.public_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_student_representative_can_view_common_page(self):
        self.sign_in_as_student_representative()
        response = self.client.get(self.common_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_student_representative_can_view_private_page(self):
        self.sign_in_as_student_representative()
        response = self.client.get(self.private_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_super_user_can_view_all_pages(self):
        self.sign_in_as_super_user()
        response = self.client.get(self.public_page.url, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.common_page.url, follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(self.private_page.url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_document_view(self):
        self.common_page.attachments.add(self.first_document)
        self.common_page.save()
        self.private_page.attachments.add(self.second_document)
        self.private_page.save()

        self.sign_in_as_student()
        response = self.client.get(self.first_document.url, follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(self.second_document.url, follow=True)
        self.assertEqual(response.status_code, 403)
