from .tenca_test import TencaTest


class ListTest(TencaTest):

    testlist_name = "testlist"

    creator_name = TencaTest.email("thecreator")
    p2_name = TencaTest.email("person2")

    def addresses(self, memberlist):
        return [str(member.address) for member in memberlist]

    def assertMembers(self, memberlist, attr_name="members"):
        attr = getattr(self.testlist.list, attr_name)
        self.assertSortedListEqual(memberlist, self.addresses(attr))

    def setUp(self):
        super().setUp()
        self.clear_testlist(self.testlist_name)
        self.testlist = self.conn.add_list(self.testlist_name, self.creator_name)

    def tearDown(self):
        super().tearDown()
        self.clear_testlist(self.testlist_name)
