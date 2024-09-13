from ...tenca_django.connection import Connection
from ...tenca_django.hash_storage import (
    DictCachedDescriptionStorage,
    HashStorage,
    MailmanDescriptionHashStorage,
    NotInStorageError,
    VolatileDictHashStorage,
)
from .tenca_test import TencaTest


class DisabledHashStorage(HashStorage):
    """No storing at all. Disables hash-lookup"""

    def get_list(self, hash_id):
        raise NotInStorageError(hash_id)

    def store_list(self, hash_id, list):
        pass

    def list_hash(self, list):
        return None

    def __contains__(self, hash_id):
        return False

    def get_list_id(self, hash_id):
        raise NotInStorageError()

    def store_list_id(self, hash_id, list_id):
        pass

    def get_hash_id(self, list_id):
        raise NotInStorageError(list_id)

    def delete_hash_id(self, hash_id):
        pass

    def hashes(self):
        return iter([])


class HiddenFromTestRunner(object):

    class HashStorageTest(TencaTest):

        StorageClass = DisabledHashStorage

        # Assumes stable hash_id creation
        test_data = {
            # list_id: hash_id
            TencaTest.list_id("list_a"): "ALongLookingHashId1",
            TencaTest.list_id("list_b"): "ALongLookingHashId2",
            TencaTest.list_id("list_c"): "ALongLookingHashId3",
        }

        get_list_test_data = (TencaTest.list_id("list_d"), "ALongLookingHashId4")

        def shortname(self, list_id):
            return list_id.split(".", 1)[0]

        def setUp(self):
            self.conn = Connection(DisabledHashStorage)
            self.hash_storage = self.StorageClass(self.conn)

            for listname in self.test_data:
                self.clear_testlist(listname)

            get_list_test_id = self.get_list_test_data[0]
            self.clear_testlist(get_list_test_id)
            self.conn.domain.create_list(self.shortname(get_list_test_id))

        def storeTestData(self):
            for list_id, hash_id in self.test_data.items():
                self.hash_storage.store_list_id(hash_id, list_id)

        def testStoreAndRetrieveIds(self, store_test_data=True):
            if store_test_data:
                self.storeTestData()
            for list_id, hash_id in self.test_data.items():
                self.assertEqual(list_id, self.hash_storage.get_list_id(hash_id))
                self.assertEqual(hash_id, self.hash_storage.get_hash_id(list_id))

        def testHashList(self, store_test_data=True):
            if store_test_data:
                self.storeTestData()
            self.assertSortedListEqual(
                list(self.test_data.values()), list(self.hash_storage.hashes())
            )

        def testGetList(self):
            test_list_id, test_hash_id = self.get_list_test_data

            self.hash_storage.store_list_id(test_hash_id, test_list_id)
            received_l = self.hash_storage.get_list(test_hash_id)

            self.assertEqual(test_list_id, received_l.list_id)
            with self.assertRaises(NotInStorageError):
                self.hash_storage.get_list("Invalid_Hash")
            with self.assertRaises(NotInStorageError):
                self.hash_storage._raw_conn_getlist("Invalid_ListName")

        def testRealGetList(self):
            test_list_id, test_hash_id = self.get_list_test_data
            self.hash_storage.store_list_id(test_hash_id, test_list_id)

            retain_dummy_hash_storage = self.conn.hash_storage
            try:
                self.conn.hash_storage = self.hash_storage
                received_l = self.conn.get_list_by_hash_id(test_hash_id)
                self.assertEqual(test_list_id, received_l.list_id)
                self.assertEqual(test_hash_id, received_l.hash_id)
                self.assertEqual(test_hash_id, self.hash_storage.list_hash(received_l.list))

                self.assertIsNone(self.conn.get_list_by_hash_id("Invalid_Hash"))
            finally:
                self.conn.hash_storage = retain_dummy_hash_storage

        def testStoreList(self, create_list=True):
            test_list_id, test_hash_id = self.get_list_test_data
            list = self.conn.client.get_list(test_list_id)

            self.hash_storage.store_list(test_hash_id, list)
            self.assertEqual(self.hash_storage.get_hash_id(test_list_id), test_hash_id)

        def testContains(self, store_test_data=True):
            if store_test_data:
                self.storeTestData()
            for hash_id in self.test_data.values():
                self.assertIn(hash_id, self.hash_storage)

        def testNotInStorage(self):
            self.assertNotIn("Invalid_Hash", self.hash_storage)
            with self.assertRaises(NotInStorageError):
                self.hash_storage.get_list_id("Invalid_Hash")
            with self.assertRaises(NotInStorageError):
                self.hash_storage.get_list("Invalid_Hash")
            with self.assertRaises(NotInStorageError):
                self.hash_storage.get_hash_id("Invalid_ListName")

        def testHashDeletion(self, store_test_data=True):
            if store_test_data:
                self.storeTestData()
            list_a_hash = self.hash_storage.get_hash_id(TencaTest.list_id("list_a"))

            self.hash_storage.delete_hash_id(list_a_hash)
            self.assertNotIn(list_a_hash, self.hash_storage)

        def tearDown(self):
            for listname in self.test_data:
                self.clear_testlist(listname)
            self.clear_testlist(self.get_list_test_data[0])


class VolatileDictHashStorageTest(HiddenFromTestRunner.HashStorageTest):
    StorageClass = VolatileDictHashStorage


class MailmanDescriptionHashStorageTest(HiddenFromTestRunner.HashStorageTest):
    StorageClass = MailmanDescriptionHashStorage

    def setUp(self):
        super().setUp()
        # MailmanDescriptionHashStorage requires lists to be
        # present in the Mailman backend
        for list_id in self.test_data:
            self.conn.domain.create_list(self.shortname(list_id))

    def assertIsSubset(self, sub, super):
        self.assertTrue(sub.issubset(super))

    def testHashList(self, store_test_data=True):
        # For reasons, we do not want to drop all
        # lists on the current running Mailman instance.
        # So, do a subset test instead.
        if store_test_data:
            self.storeTestData()
        self.assertIsSubset(set(self.test_data.values()), set(self.hash_storage.hashes()))

    def testSilentDeletionAndStorage(self):
        # MailmanDescriptionHashStorage breaks LSP by silently discarding
        # values, if list does not exist
        self.hash_storage.store_list_id("NonExistentHash", "non_existent_list")
        self.assertNotIn("NonExistentHash", self.hash_storage)

        self.assertIsNone(self.hash_storage.delete_hash_id("Invalid_Hash"))

    def testInvalidDescription(self):
        # So far the test_data lists exist, but have no description set
        for list_id in self.test_data:
            list = self.conn.client.get_list(self.conn.fqdn_ize(list_id))
            with self.assertRaises(NotInStorageError):
                self.hash_storage.list_hash(list)


class DictCachedDescriptionStorageTest(MailmanDescriptionHashStorageTest):
    StorageClass = DictCachedDescriptionStorage

    def storeAndClearL1(self):
        self.storeTestData()
        self.hash_storage.l1._d.clear()

    def testStoreAndRetrieveIdsFromL2(self):
        self.storeAndClearL1()
        self.testStoreAndRetrieveIds(False)
        # Test that the data is now in dict L1
        for hash_id in self.test_data.values():
            self.assertIn(hash_id, self.hash_storage.l1)

    def testHashListOfL2(self):
        self.storeAndClearL1()
        self.testHashList(False)

    def testContainsInL2(self):
        self.storeAndClearL1()
        self.testContains(False)

    def testHashDeletionFromL2(self):
        self.storeAndClearL1()
        self.testHashDeletion(False)

    def testFlush(self):
        self.storeTestData()
        new_list_a_hash = "ANewlyOverwrittenHash"
        list_a_id = TencaTest.list_id("list_a")

        self.hash_storage.l1.store_list_id(
            new_list_a_hash,
            list_a_id,
        )
        self.assertNotEqual(new_list_a_hash, self.hash_storage.l2.get_hash_id(list_a_id))
        self.hash_storage.flush(new_list_a_hash)
        self.assertEqual(new_list_a_hash, self.hash_storage.l2.get_hash_id(list_a_id))

    def testSilentDeletionAndStorage(self):
        # Breaks LSP again, as dict retains values
        pass
