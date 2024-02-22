from django.conf import settings
from django.db.models import Q
from wagtail.models import Site

from .models import BasePage, MinutesList
from .utils import get_user_groups


def base_context(request):
    # How wagtail page trees work: https://www.accordbox.com/blog/how-to-create-and-manage-menus-in-wagtail/

    # Fetch all pages
    root_page = getattr(Site.find_for_request(request), "root_page", None)
    pages = BasePage.objects.live()

    if not root_page:
        return {"root_page": None, "pages_by_parent": None}

    # Determine the correct root for the active language
    root_page = root_page.localized

    # Determine all pages the user may view based on his groups
    user_groups = get_user_groups(request.user)

    pages_visible_for_user = pages.filter(
        (Q(visible_for__in=user_groups) | Q(is_public=True))
        & (Q(show_in_menus=True) | Q(id=root_page.id))
    ).distinct()

    page_lookup = {}

    for page in pages_visible_for_user:
        page_lookup[page.path] = pages_visible_for_user.child_of(page).order_by("path")

    minutes_creation_links = {}
    for group in request.user.groups.all():
        minutes_creation_links[group.id] = create_minutes_for_group_link(request.user, group)

    return {
        "root_page": root_page,
        "pages_by_parent": page_lookup,
        "minutes_creation_links": minutes_creation_links,
        "template_cache_duration": 1 if settings.DEBUG else 500,
    }


def create_minutes_for_group_link(user, group):
    minutes_list = MinutesList.objects.filter(group=group).first()
    if not minutes_list:
        return None
    if minutes_list.permissions_for_user(user).can_add_subpage():
        from django.urls import reverse

        return reverse("wagtailadmin_pages:add_subpage", kwargs={"parent_page_id": minutes_list.id})
