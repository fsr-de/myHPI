import unittest

from myhpi.tenca_django.connection import Connection


class TencaTest(unittest.TestCase):

    def email(name):
        return "{}@example.com".format(name)

    def list_id(name):
        return "{}.lists.example.com".format(name)

    def assertSortedListEqual(self, first, second):
        self.assertListEqual(list(sorted(first)), list(sorted(second)))

    def setUp(self):
        self.conn = Connection()

    def clear_testlist(self, listname, *args, **kwargs):
        self.conn.delete_list(listname, *args, **kwargs)
