import urllib.error

from myhpi.tenca_django import exceptions

from .list_test import ListTest


class TestConfirmation(ListTest):

    def testHasSubscriptionToken(self):
        token = self.testlist.add_member(self.p2_name)
        self.assertDictEqual({token: self.p2_name}, self.testlist.pending_subscriptions())

    def testHasSubscriptionTokenPreMM3_3_3(self):
        # Test mailmanclient-based request fetch (for mailmancore<3.3.3)
        with settings.TemporarySettingsChange(DISABLE_GOODBYE_MESSAGES=False):
            self.testHasSubscriptionToken()

    def testNonSilentAddition(self):
        token = self.testlist.add_member(self.p2_name)
        self.assertMembers([self.creator_name])
        self.assertDictEqual(self.testlist.pending_subscriptions(), {token: self.p2_name})

        self.testlist.confirm_subscription(token)
        self.assertMembers([self.creator_name, self.p2_name])
        self.assertDictEqual(self.testlist.pending_subscriptions(), {})

    def testToggleMembership(self):
        status, token = self.testlist.toggle_membership(self.p2_name)
        self.assertTrue(status)
        self.testlist.confirm_subscription(token)
        self.assertMembers([self.creator_name, self.p2_name])

        status, token = self.testlist.toggle_membership(self.p2_name)
        self.assertFalse(status)
        self.testlist.confirm_subscription(token)
        self.assertMembers([self.creator_name])

    def testCancelPendingAddition(self):
        token = self.testlist.add_member(self.p2_name)
        self.testlist.cancel_pending_subscription(token)
        self.assertMembers([self.creator_name])
        self.assertDictEqual(self.testlist.pending_subscriptions(), {})

    def testNonExistentRequests(self):
        with self.assertRaises(exceptions.NoSuchRequestException):
            self.testlist.confirm_subscription("Does Not Exists")
        with self.assertRaises(exceptions.NoSuchRequestException):
            self.testlist.cancel_pending_subscription("Does Not Exists")

    def testNonSilentRemoval(self):
        self.testlist.add_member_silently(self.p2_name)
        token = self.testlist.remove_member(self.p2_name)
        self.assertMembers([self.creator_name, self.p2_name])
        ## Assertion removed, as of MailmanCore<3.3.3 pending dict will be empty
        # self.assertDictEqual(
        # 	self.testlist.pending_subscriptions(),
        # 	{token: self.p2_name}
        # )

        self.testlist.confirm_subscription(token)
        self.assertMembers([self.creator_name])
        self.assertDictEqual(self.testlist.pending_subscriptions(), {})

    def testCancelOnReRequest(self):
        with settings.TemporarySettingsChange(RETRY_CANCELS_PENDING_SUBSCRIPTION=True):
            token = self.testlist.add_member(self.p2_name)
            self.assertMembers([self.creator_name])
            self.assertDictEqual(self.testlist.pending_subscriptions(), {token: self.p2_name})
            token2 = self.testlist.add_member(self.p2_name)
            self.assertMembers([self.creator_name])
            self.assertDictEqual(self.testlist.pending_subscriptions(), {token2: self.p2_name})
            self.testlist.confirm_subscription(token2)
            self.assertMembers([self.creator_name, self.p2_name])

    def testFailOnReRequest(self):
        with settings.TemporarySettingsChange(RETRY_CANCELS_PENDING_SUBSCRIPTION=False):
            token = self.testlist.add_member(self.p2_name)
            self.assertMembers([self.creator_name])
            self.assertDictEqual(self.testlist.pending_subscriptions(), {token: self.p2_name})
            with self.assertRaisesRegex(urllib.error.HTTPError, "already pending"):
                token2 = self.testlist.add_member(self.p2_name)
            self.assertDictEqual(self.testlist.pending_subscriptions(), {token: self.p2_name})
