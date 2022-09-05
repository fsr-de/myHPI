from myhpi.tests.core.utils import MyHPIPageTestCase


class MinutesTests(MyHPIPageTestCase):
    def test_minutes_links_to_neighboring_minutes(self):
        self.sign_in_as_student()
        minutes = self.client.get(
            "/en/student-representation/fsr/minutes/second-minutes", follow=True
        )
        self.assertInHTML("< Previous minutes", minutes.rendered_content)
        self.assertInHTML("Next minutes >", minutes.rendered_content)

        self.assertIn("first-minutes", minutes.rendered_content)
        self.assertNotIn("private-minutes", minutes.rendered_content)
        self.assertNotIn("unpublished-minutes", minutes.rendered_content)
        self.assertIn("recent-minutes", minutes.rendered_content)

    def test_minutes_links_to_neighboring_minutes_for_student_representatives(self):
        self.sign_in_as_student_representative()
        minutes = self.client.get(
            "/en/student-representation/fsr/minutes/second-minutes", follow=True
        )
        self.assertInHTML("< Previous minutes", minutes.rendered_content)
        self.assertInHTML("Next minutes >", minutes.rendered_content)

        self.assertIn("first-minutes", minutes.rendered_content)
        self.assertIn("private-minutes", minutes.rendered_content)
        self.assertNotIn("unpublished-minutes", minutes.rendered_content)
        self.assertNotIn("recent-minutes", minutes.rendered_content)

    def test_most_recent_minutes_does_not_have_link_to_next_minutes(self):
        self.sign_in_as_student()
        minutes = self.client.get(
            "/en/student-representation/fsr/minutes/recent-minutes", follow=True
        )
        self.assertNotIn("Next minutes >", minutes.rendered_content)
        self.assertInHTML("< Previous minutes", minutes.rendered_content)

    def test_oldest_minutes_does_not_have_link_to_previous_minutes(self):
        self.sign_in_as_student()
        minutes = self.client.get(
            "/en/student-representation/fsr/minutes/first-minutes", follow=True
        )
        self.assertNotIn("< Previous minutes", minutes.rendered_content)
        self.assertInHTML("Next minutes >", minutes.rendered_content)
