import urllib.parse

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from myhpi.tenca_django.models import HashEntry


@admin.register(HashEntry)
class HashEntryAdmin(admin.ModelAdmin):
    list_display = ("list_id", "hash_id", "link_manage_page")
    search_fields = ("list_id",)
    readonly_fields = ("list_id",)

    def _link(self, text, url):
        return format_html('<a href="{}">{}</a>'.format(url, text))

    def link_manage_page(self, obj):
        return self._link(
            _("Manage List"), reverse("tenca_django:tenca_manage_list", args=(obj.list_id,))
        )

    link_manage_page.short_description = "Management Page"

    def has_delete_permission(self, request, obj=None):
        return False
