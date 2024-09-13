from .list_test import ListTest


class TestRoles(ListTest):

    p3_name = ListTest.email("person3")

    def testPropertyDefaults(self):
        self.assertTrue(self.testlist.notsubscribed_allowed_to_post)
        self.assertFalse(self.testlist.replies_addressed_to_list)

    # Missing: Access e-mails to check effects

    def testNotSubscribedAllowedToPostToggle(self):
        self.testlist.notsubscribed_allowed_to_post = True
        self.assertTrue(self.testlist.notsubscribed_allowed_to_post)
        self.testlist.notsubscribed_allowed_to_post = False
        self.assertFalse(self.testlist.notsubscribed_allowed_to_post)
        self.testlist.notsubscribed_allowed_to_post = True
        self.assertTrue(self.testlist.notsubscribed_allowed_to_post)
        self.assertEqual(self.testlist.list.settings["default_nonmember_action"], "accept")

    def testRepliesAddressedToListToggle(self):
        self.testlist.replies_addressed_to_list = True
        self.assertTrue(self.testlist.replies_addressed_to_list)
        self.testlist.replies_addressed_to_list = False
        self.assertFalse(self.testlist.replies_addressed_to_list)
        self.testlist.replies_addressed_to_list = True
        self.assertTrue(self.testlist.replies_addressed_to_list)


class TestHashsAndInjection(ListTest):

    def testUpdatingInviteLink(self):
        old_hash_id = self.testlist.hash_id
        new_hash_id = "AnotherLinkToClick"

        def get_template(name):
            for t in self.testlist.list.templates:
                if t.name == name:
                    return t.uri

        footer_link = get_template("list:member:regular:footer")
        self.assertIn(old_hash_id, footer_link)
        self.assertNotIn(new_hash_id, footer_link)

        self.conn.hash_storage.store_list_id(new_hash_id, self.testlist.list_id)
        self.conn.flush_hash(new_hash_id)

        footer_link = get_template("list:member:regular:footer")
        self.assertIn(new_hash_id, footer_link)
        self.assertNotIn(old_hash_id, footer_link)

    def testHashProposalStable(self):
        with settings.TemporarySettingsChange(USE_RANDOM_LIST_HASH=False):
            previous_hashes = []
            for round in range(3):
                hash1 = self.testlist.propose_hash_id(round)
                hash2 = self.testlist.propose_hash_id(round)
                self.assertEqual(hash1, hash2)
                self.assertNotIn(hash1, previous_hashes)
                previous_hashes.append(hash1)

    def testRandomHashRandom(self):
        """Very unlikely, but might fail. It's __random__."""
        with settings.TemporarySettingsChange(USE_RANDOM_LIST_HASH=True):
            previous_hashes = []
            for round in range(3):
                hash1 = self.testlist.propose_hash_id(round)
                hash2 = self.testlist.propose_hash_id(round)
                self.assertNotEqual(hash1, hash2)
                self.assertNotIn(hash1, previous_hashes)
                previous_hashes.append(hash1)
                previous_hashes.append(hash2)

    def testInjectRunsWithOutExceptions(self):
        self.testlist.inject_message(
            self.creator_name,
            "A Test Subject",
            "\n".join(
                [
                    "Hi,",
                    "good news: As a testrunner I could inject a message.",
                    "Now check that it is there (including footer), and not merely bump coverage.",
                ]
            ),
            other_headers={"CC": self.p2_name},
        )
