from django.test import Client, TestCase

from myhpi.tests.core.setup import setup_data


class MyHPIPageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_data = setup_data()

        self.root_page = self.test_data["basic_pages"]["root_page"]
        self.information_menu = self.test_data["basic_pages"]["information_menu"]
        self.student_representation_menu = self.test_data["basic_pages"][
            "student_representation_menu"
        ]
        self.fsr_menu = self.test_data["basic_pages"]["fsr_menu"]

        self.common_page = self.test_data["pages"][0]
        self.private_page = self.test_data["pages"][1]
        self.public_page = self.test_data["pages"][2]
        self.hidden_public_page = self.test_data["pages"][3]

        self.minutes = self.test_data["minutes"]
        self.student_representative_group_minutes = self.test_data["minutes_list"]

        self.super_user = self.test_data["users"][0]
        self.student = self.test_data["users"][1]
        self.student_representative = self.test_data["users"][2]

        self.first_document = self.test_data["documents"][0]
        self.second_document = self.test_data["documents"][1]

    def sign_in_as_student(self):
        self.client.force_login(self.student)

    def sign_in_as_student_representative(self):
        self.client.force_login(self.student_representative)

    def sign_in_as_super_user(self):
        self.client.force_login(self.super_user)
