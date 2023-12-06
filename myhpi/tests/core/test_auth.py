from myhpi.core.auth import MyHPIOIDCAB
from myhpi.tests.core.utils import MyHPIPageTestCase


class AuthTests(MyHPIPageTestCase):
    def setUp(self):
        super().setUp()
        self.auth_backend = MyHPIOIDCAB()

    def test_create_user(self):
        claims = {
            "email": "ali.gator@example.org",
            "given_name": "Ali",
            "family_name": "Gator",
            "sub": "ali.gator",
        }
        user = self.auth_backend.create_user(claims)
        self.assertEqual(user.username, "ali.gator")
        self.assertFalse(user.groups.filter(name="Student").exists())

        matching_users = self.auth_backend.filter_users_by_claims(claims)
        self.assertEqual(len(matching_users), 1)

    def test_create_student(self):
        claims = {
            "email": "grace.hopper@student.uni-potsdam.example.com",
            "given_name": "Grace",
            "family_name": "Hopper",
            "sub": "grace.hopper",
        }
        user = self.auth_backend.create_user(claims)
        self.assertEqual(user.username, "grace.hopper")
        self.assertEqual(user.email, "grace.hopper@student.uni-potsdam.example.com")

    def test_update_user(self):
        claims = {
            "email": "jw.goethe@weimar.de",
            "given_name": "Johann Wolfgang",
            "family_name": "Goethe",
            "sub": "jw.goethe",
        }
        user = self.auth_backend.create_user(claims)
        self.assertEqual(user.username, "jw.goethe")
        self.assertEqual(user.last_name, "Goethe")
        claims["family_name"] = "von Goethe"
        claims["email"] = "jw.goethe@weimar.eu"
        user = self.auth_backend.update_user(user, claims)
        self.assertEqual(user.first_name, "Johann Wolfgang")
        self.assertEqual(user.last_name, "von Goethe")
        self.assertEqual(user.email, "jw.goethe@weimar.eu")
