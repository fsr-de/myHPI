from ...tenca_django import exceptions
from .list_test import ListTest


class TestRoles(ListTest):

    p3_name = ListTest.email("person3")
    nh_name = ListTest.email("not_here")

    def testFQDNInListInfo(self):
        self.assertIn(self.testlist.fqdn_listname, repr(self.testlist))

    def testSilentAddition(self):
        self.assertFalse(self.testlist.is_member(self.p2_name))
        self.assertFalse(self.testlist.is_member(self.p3_name))
        self.testlist.add_member_silently(self.p2_name)
        self.testlist.add_member_silently(self.p3_name)
        self.assertMembers([self.creator_name, self.p2_name, self.p3_name])
        self.assertTrue(self.testlist.is_member(self.p2_name))
        self.assertTrue(self.testlist.is_member(self.p3_name))

    def testRemoval(self):
        self.testSilentAddition()
        self.testlist.remove_member_silently(self.p2_name)
        self.assertMembers([self.creator_name, self.p3_name])
        with self.assertRaises(exceptions.NoMemberException):
            self.testlist.remove_member_silently(self.nh_name)
        with self.assertRaises(exceptions.LastOwnerException):
            self.testlist.remove_member_silently(self.creator_name)

    def testPromotionAndDemotion(self):
        self.testSilentAddition()
        self.assertFalse(self.testlist.is_owner(self.p2_name))
        self.assertMembers([self.creator_name], "owners")
        self.testlist.promote_to_owner(self.p2_name)

        self.assertTrue(self.testlist.is_owner(self.p2_name))
        self.assertMembers([self.creator_name, self.p2_name], "owners")

    def testDemotion(self):
        self.testPromotionAndDemotion()
        self.testlist.remove_member_silently(self.creator_name)
        self.assertMembers([self.p2_name], "owners")
        with self.assertRaises(exceptions.NoMemberException):
            self.testlist.demote_from_owner(self.p3_name)

    def testBlocking(self):
        # Missing: Access e-mails to check effects
        self.testlist.add_member_silently(self.p2_name)
        self.assertFalse(self.testlist.is_blocked(self.p2_name))
        self.testlist.set_blocked(self.p2_name, True)
        self.assertTrue(self.testlist.is_blocked(self.p2_name))
        self.testlist.set_blocked(self.p2_name, False)
        self.assertFalse(self.testlist.is_blocked(self.p2_name))

    def testBlockingFailsOnNonmember(self):
        with self.assertRaises(exceptions.NoMemberException):
            self.testlist.set_blocked(self.nh_name, True)

    def testRoster(self):
        self.testlist.add_member_silently(self.p2_name)
        self.testlist.add_member_silently(self.p3_name)
        self.testlist.set_blocked(self.p2_name, True)

        self.assertSortedListEqual(
            list(self.testlist.get_roster()),
            [
                (self.creator_name, (True, False)),
                (self.p2_name, (False, True)),
                (self.p3_name, (False, False)),
            ],
        )

        self.testlist.set_blocked(self.p2_name, False)
        self.testlist.promote_to_owner(self.p2_name)
        self.assertSortedListEqual(
            list(self.testlist.get_roster()),
            [
                (self.creator_name, (True, False)),
                (self.p2_name, (True, False)),
                (self.p3_name, (False, False)),
            ],
        )

    def testRosterOnDeletedListCaught(self):
        self.testlist.add_member_silently(self.p2_name)
        self.clear_testlist(self.testlist_name)
        self.assertListEqual(self.testlist._raw_get_roster("member"), [])
