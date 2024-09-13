from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from myhpi.tenca_django.hash_storage import HashStorage, NotInStorageError, TwoLevelHashStorage, \
    MailmanDescriptionHashStorage


class TencaModel(models.Model):
    class Meta:
        abstract = True
        app_label = "tenca_django"


class HashEntry(TencaModel):
    hash_id = models.CharField(max_length=64, unique=True, blank=False, null=False)
    list_id = models.CharField(max_length=128, blank=False, null=False)

    def __str__(self):
        return "HashEntry for {}".format(self.list_id)

    @property
    def manage_page(self):
        return format_html(
            '<a href="{url}">{text}</a>'.format(
                text=_("Manage List"),
                url=reverse("tenca_django:tenca_manage_list", args=(self.list_id,)),
            )
        )

    class Meta(TencaModel.Meta):
        verbose_name = "Mailing List Hash Entry"
        verbose_name_plural = "Mailing List Hash Entries"


class DjangoModelHashStorage(HashStorage):
    def __contains__(self, hash_id):
        try:
            HashEntry.objects.get(hash_id=hash_id)
            return True
        except HashEntry.DoesNotExist:
            return False

    def get_list_id(self, hash_id):
        try:
            entry = HashEntry.objects.get(hash_id=hash_id)
        except HashEntry.DoesNotExist:
            raise NotInStorageError()
        else:
            return entry.list_id

    def store_list_id(self, hash_id, list_id):
        entry = HashEntry(hash_id=hash_id, list_id=list_id)
        entry.save()

    def get_hash_id(self, list_id):
        try:
            entry = HashEntry.objects.get(list_id=list_id)
        except HashEntry.DoesNotExist:
            raise NotInStorageError()
        else:
            return entry.hash_id

    def delete_hash_id(self, hash_id):
        try:
            entry = HashEntry.objects.get(hash_id=hash_id)
        except HashEntry.DoesNotExist:
            pass
        else:
            entry.delete()

    def hashes(self):
        return (e.hash_id for e in HashEntry.objects.all())


class DjangoModelCachedDescriptionHashStorage(TwoLevelHashStorage):
    l1_class = DjangoModelHashStorage
    l2_class = MailmanDescriptionHashStorage
