from django.db.models import Q
from wagtail.core.models import Site

from .models import BasePage
from .utils import get_user_groups


def base_context(request):
    # How wagtail page trees work: https://www.accordbox.com/blog/how-to-create-and-manage-menus-in-wagtail/

    # Fetch all pages
    root_page = getattr(Site.find_for_request(request), "root_page", None)
    pages = BasePage.objects.live()

    if not root_page:
        return {"root_page": None, "pages_by_parent": None}

    # Determine all pages the user may view based on his groups
    user_groups = get_user_groups(request.user)

    pages_visible_for_user = pages.filter(
        (Q(visible_for__in=user_groups) | Q(is_public=True))
        & (Q(show_in_menus=True) | Q(id=root_page.id))
    ).distinct()

    page_lookup = {}

    for page in pages_visible_for_user:
        page_lookup[page.path] = pages_visible_for_user.child_of(page)

    return {
        "root_page": root_page,
        "pages_by_parent": page_lookup,
    }
