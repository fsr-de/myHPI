from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from myhpi.tenca_django.models import HashEntry


class HashEntryFilterSet(SnippetViewSet):
    model = HashEntry
    add_to_admin_menu = True
    menu_label = _("Mailing Lists")
    menu_icon = "mail"
    list_display = ("list_id", "hash_id", "manage_page")

    edit_handler = MultiFieldPanel(
        [
            FieldPanel("list_id", read_only=True),
            FieldPanel("hash_id"),
        ]
    )


register_snippet(HashEntryFilterSet)
