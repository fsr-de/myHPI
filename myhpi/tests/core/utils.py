from django.test import Client, TestCase

from myhpi.tests.core.setup import setup_data


class MyHPIPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_data = setup_data()
        self.common_page = self.test_data["pages"][0]
        self.private_page = self.test_data["pages"][1]
        self.public_page = self.test_data["pages"][2]
        self.student = self.test_data["users"][1]
        self.student_representative = self.test_data["users"][2]

    def sign_in_as_student(self):
        self.client.force_login(self.student)

    def sign_in_as_student_representative(self):
        student_representative = self.test_data["users"][2]
        self.client.force_login(self.student_representative)
