import urllib.error

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from mailmanclient.restbase.connection import MailmanConnectionError

import itertools
import urllib.error

import mailmanclient

from myhpi.tenca_django import exceptions
from myhpi.tenca_django.hash_storage import NotInStorageError, DictCachedDescriptionStorage
from myhpi.tenca_django.mailinglist import MailingList
from myhpi.tenca_django.models import DjangoModelCachedDescriptionHashStorage


class FakeConnection:
    def __init__(self, exception):
        self.exception = exception

    def __getattr__(self, name):
        raise self.exception


class Connection(object):
    """A decorator for mailmanclient.Client"""

    def __init__(self, hash_storage_cls=None):
        """Creates a new connection to Mailman's REST API.

        Can be provided with a subclass of tenca.HashStorage to lookup
        scrambled hashes, identifying a mailing list in the invite links.

        If hash_storage_cls is None, DjangoModelCachedDescriptionHashStorage will be used.
        """
        self.client = mailmanclient.Client(
            settings.TENCA_MAILMAN_URL, settings.TENCA_ADMIN_USER, settings.TENCA_ADMIN_PASS
        )
        domains = self.client.domains
        assert len(domains), 1
        self.domain = domains[0]
        if hash_storage_cls is None:
            hash_storage_cls = DjangoModelCachedDescriptionHashStorage
        assert hash_storage_cls is not None
        self.hash_storage = hash_storage_cls(self)

    def __repr__(self):
        return "<{} on {} for {}>".format(
            type(self).__name__, settings.TENCA_MAILMAN_URL, str(self.domain)
        )

    def _wrap_list(self, list, skip_hash_id=False, hash_id=None):
        if hash_id is None:
            try:
                hash_id = None if skip_hash_id else self.hash_storage.list_hash(list)
            except NotInStorageError:
                hash_id = None
        return MailingList(self, list, hash_id)

    def rest_call(self, path, data=None, method=None):
        return self.client._connection.call(path, data, method)

    def fqdn_ize(self, listname):
        if "@" in listname:
            return listname
        domain_str = "." + str(self.domain)
        if listname.endswith(domain_str):
            listname = listname.rsplit(domain_str, 1)[0]
        return "{}@{}".format(listname, str(self.domain))

    def get_list(self, fqdn_listname):
        try:
            return self._wrap_list(self.client.get_list(fqdn_listname))
        except urllib.error.HTTPError as e:
            exceptions.map_http_404(e)
            return None

    def get_list_by_hash_id(self, hash_id):
        try:
            return self._wrap_list(self.hash_storage.get_list(hash_id), hash_id=hash_id)
        except NotInStorageError:
            # TODO: Discard hash if in storage? What's the fastest way?
            return None

    def _create_list(self, name, creator_email, hash_id):
        new_list = self.domain.create_list(name)

        wrapped_list = self._wrap_list(new_list, skip_hash_id=True)
        wrapped_list.configure_list()

        if hash_id is None:
            proposals = (wrapped_list.propose_hash_id(round) for round in itertools.count())
            for proposed_hash_id in proposals:
                if proposed_hash_id not in self.hash_storage:
                    hash_id = proposed_hash_id
                    break

        wrapped_list.hash_id = hash_id
        self.hash_storage.store_list(hash_id, new_list)
        wrapped_list.configure_templates()

        if creator_email is not None:
            wrapped_list.add_member_silently(creator_email)
            wrapped_list.promote_to_owner(creator_email)

        return wrapped_list

    def flush_hash(self, hash_id):
        """Call this function, when you manually changed a list's hash_id in your UI.

        This will cause two actions:
                * In a multi-level cache write the hash to all storages
                * Issue a reload of the list's text templates
        """
        self.hash_storage.flush(hash_id)
        mailing_list = self.get_list_by_hash_id(hash_id)
        if mailing_list:
            mailing_list.configure_templates()

    def import_eemaill(self, name, hash_id):
        """Adds a list and directly assigns an hash_id (good for imports)"""
        return self._create_list(name, creator_email=None, hash_id=hash_id)

    def add_list(self, name, creator_email):
        """Adds a list and sets the first member and creator as owner"""
        return self._create_list(name, creator_email, hash_id=None)

    def delete_list(self, listname, silent_fail=True, retain_hash=False):
        if not retain_hash:
            l = self.get_list(self.fqdn_ize(listname))
            if l is None:
                if silent_fail:
                    return
                raise exceptions.TencaException("No such list")
            fqdn = l.fqdn_listname
            self.hash_storage.delete_hash_id(l.hash_id)
        else:
            fqdn = self.fqdn_ize(listname)
        try:
            self.client.delete_list(fqdn)
        except urllib.error.HTTPError as e:
            exceptions.map_http_404(e, None if silent_fail else exceptions.TencaException)

    def _raw_find_lists(self, addresses, role):
        for address in addresses:
            data = {"subscriber": address, "role": role}
            try:
                response, content = self.rest_call("lists/find", data)
                if "entries" not in content:
                    yield []
            except urllib.error.HTTPError as e:
                exceptions.map_http_404(e)
                yield []
            else:
                yield [entry["list_id"] for entry in content["entries"]]

    def find_lists(self, address, role=None, count=50, page=1):
        """Returns a paginated view on all lists address is member of"""
        try:
            return [
                self._wrap_list(list) for list in self.client.find_lists(address, role, count, page)
            ]
        except urllib.error.HTTPError as e:
            exceptions.map_http_404(e)
            return []

    def get_owner_and_memberships(self, *addresses, ignore_missing_hashes=False):
        """Returns a list of tuples in the form (MailingList, bool),
        for all lists address is a member of, with the second argument being tur,
        if that member is also an owner of the MailingList.

        The resulted is sorted alphabetically, with the owned lists first.
        """
        memberships = {
            list_id: False
            for list_id in itertools.chain(*self._raw_find_lists(addresses, "member"))
        }
        memberships.update(
            {
                list_id: True
                for list_id in itertools.chain(*self._raw_find_lists(addresses, "owner"))
            }
        )
        sorted_mo_ships = sorted(
            memberships.items(), key=lambda t: (not t[1], t[0])
        )  # False < True
        result = []
        for list_id, is_owner in sorted_mo_ships:
            try:
                result.append((list_id, self.hash_storage.get_hash_id(list_id), is_owner))
            except NotInStorageError as e:
                if not ignore_missing_hashes:
                    raise e
        return result

    def mark_address_verified(self, address):
        try:
            addr = self.client.get_address(address)
        except urllib.error.HTTPError as e:
            exceptions.map_http_404(e, exceptions.NoMemberException)
        else:
            addr.verify()


try:
    connection = Connection()
except (MailmanConnectionError, AttributeError) as e:
    connection = FakeConnection(ImproperlyConfigured(*e.args))
except urllib.error.HTTPError as e:
    connection = FakeConnection(ImproperlyConfigured(str(e)))
