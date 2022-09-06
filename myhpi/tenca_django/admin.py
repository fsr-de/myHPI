from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from myhpi.tenca_django.models import HashEntry


def _link(text, url):
    return format_html('<a href="{}">{}</a>'.format(url, text))


class HashEntryAdmin(ModelAdmin):
    model = HashEntry
    menu_label = "Mailing Lists"
    menu_icon = "mail"
    add_to_settings_menu = True
    list_display = ("list_id", "hash_id", "link_manage_page")

    def link_manage_page(self, obj):
        return _link(
            _("Manage List"), reverse("tenca_django:tenca_manage_list", args=(obj.list_id,))
        )

    link_manage_page.short_description = "Management Page"
    panels = [
        FieldPanel("hash_id"),
        # Read only would be nice, but is not yet implemented (https://github.com/wagtail/wagtail/issues/2893)
        FieldPanel("list_id", heading="List id, DO NOT EDIT!"),
    ]


modeladmin_register(HashEntryAdmin)
