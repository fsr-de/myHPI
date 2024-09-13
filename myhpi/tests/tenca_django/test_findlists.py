import itertools

from myhpi.tenca_django import exceptions

from .tenca_test import TencaTest


class TestFindLists(TencaTest):

    test_data = {
        # listname: ([creator, *other_owners], [*other_members])
        "list_a": (["thecreator"], []),
        "list_b": (["thecreator", "person2"], ["person3"]),
        "list_c": (["person2"], ["thecreator", "person3"]),
    }

    def email(self, name):
        return TencaTest.email(name)

    def plainName(self, list_fqdn_or_id, sep="@"):
        return list_fqdn_or_id.split(sep, 1)[0]

    def plainNames(self, lists, sep="@"):
        return [self.plainName(list.fqdn_listname, sep) for list in lists]

    def findLists(self, name, role):
        return self.plainNames(self.conn.find_lists(self.email(name), role))

    def assertFindLists(self, name, role, expected):
        self.assertSortedListEqual(expected, self.findLists(name, role))

    def setUp(self):
        super().setUp()
        for listname, (owners, members) in self.test_data.items():
            creator, owners = owners[0], owners[1:]
            # Clear in case it existed
            self.clear_testlist(listname)
            newlist = self.conn.add_list(listname, self.email(creator))
            for address in set(owners + members):
                newlist.add_member_silently(self.email(address))
            for address in owners:
                newlist.promote_to_owner(self.email(address))

    def testEmptyListsOfNobody(self):
        self.assertFindLists("nobody", "member", [])
        self.assertFindLists("nobody", "owner", [])

    def testPerson3IsSomeMemberButNoOwner(self):
        self.assertGreaterEqual(len(self.findLists("person3", "member")), 1)
        self.assertFindLists("person3", "owner", [])

    def testCreatorOnEveryLists(self):
        self.assertFindLists("thecreator", "owner", ["list_a", "list_b"])
        self.assertFindLists("thecreator", "member", self.test_data.keys())

    def testListDeletion(self):
        self.clear_testlist("list_a")
        self.assertFindLists("thecreator", "owner", ["list_b"])
        self.assertFindLists("thecreator", "member", ["list_b", "list_c"])

    def testNonExistentListDeletion(self):
        self.clear_testlist("does_not_exists")
        self.clear_testlist("does_not_exists", silent_fail=True, retain_hash=True)

        with self.assertRaises(exceptions.TencaException):
            self.clear_testlist("does_not_exists", silent_fail=False, retain_hash=True)
        with self.assertRaises(exceptions.TencaException):
            self.clear_testlist("does_not_exists", silent_fail=False, retain_hash=False)

    def testGetCreatorDashboard(self):
        oam = self.conn.get_owner_and_memberships(self.email("thecreator"))
        self.assertSortedListEqual(
            self.test_data.keys(),
            [self.plainName(list_id, sep=".") for list_id, _hash_id, _is_owner in oam],
        )
        self.assertTrue(
            all(
                is_owner
                for list_id, _hash_id, is_owner in oam
                if self.plainName(list_id) in ["list_a", "list_b"]
            )
        )
        self.assertFalse(
            any(
                is_owner
                for list_id, _hash_id, is_owner in oam
                if self.plainName(list_id) == "list_c"
            )
        )

    def testRawFind(self):
        self.assertListEqual(
            list(itertools.chain(*self.conn._raw_find_lists([self.email("not_here")], "member"))),
            [],
        )

    def tearDown(self):
        super().tearDown()
        for listname in self.test_data:
            self.clear_testlist(listname)
