from unittest import TestCase

from myhpi.core.utils import (
    alternative_emails,
    email_belongs_to_domain,
    replace_email_domain,
    toggle_institution,
)


class EmailUtilTest(TestCase):
    def test_email_belongs_to_domain(self):
        emails = ["abc@example.com", "abc@myhpi.de"]
        domains = ["example.com", "myhpi.de"]
        for email, domain in zip(emails, domains):
            self.assertTrue(email_belongs_to_domain(email, domain))
        self.assertFalse(email_belongs_to_domain(emails[0], domains[1]))

    def test_replace_email_domain(self):
        email = "abc@example.com"
        original_domain = "example.com"
        new_domain = "myhpi.de"
        self.assertEqual(replace_email_domain(email, original_domain, new_domain), "abc@myhpi.de")

    def test_toggle_institution(self):
        emails = ["user1@hpi.uni-potsdam.de", "user2@unrelated.com", "user3@hpi.de"]
        expected = ["user1@hpi.de", "user2@unrelated.com", "user3@hpi.uni-potsdam.de"]
        for email, expected_email in zip(emails, expected):
            toggled = list(toggle_institution(email))
            if not "unrelated" in email:
                self.assertEqual(toggled[0], expected_email)

    def test_alternative_emails(self):
        email = "user@hpi.de"
        alternatives = [
            "user@hpi.uni-potsdam.de",
            "user@student.hpi.de",
            "user@student.hpi.uni-potsdam.de",
        ]
        self.assertSetEqual(set(alternative_emails(email)), set(alternatives))
