from myhpi.tests.core.utils import MyHPIPageTestCase


class MinutesListTests(MyHPIPageTestCase):
    def test_students_can_view_some_minutes_in_minutes_list(self):
        self.sign_in_as_student()
        minutes_list = self.client.get("/en/student-representation/fsr/minutes", follow=True)
        self.assertInHTML("First minutes", minutes_list.rendered_content)
        self.assertInHTML("Second minutes", minutes_list.rendered_content)
        self.assertNotIn("Private minutes", minutes_list.rendered_content)
        self.assertNotIn("Unpublished minutes", minutes_list.rendered_content)
        self.assertInHTML("Recent minutes", minutes_list.rendered_content)

    def test_student_representatives_can_view_minutes_in_minutes_list(self):
        self.sign_in_as_student_representative()
        minutes_list = self.client.get("/en/student-representation/fsr/minutes", follow=True)
        self.assertInHTML("First minutes", minutes_list.rendered_content)
        self.assertInHTML("Second minutes", minutes_list.rendered_content)
        self.assertInHTML("Private minutes", minutes_list.rendered_content)
        self.assertInHTML("Unpublished minutes", minutes_list.rendered_content)
        self.assertInHTML("Recent minutes", minutes_list.rendered_content)
