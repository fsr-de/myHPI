from django.contrib.auth.models import Group
from django.db.models import Q
from wagtail.core.models import Page, Site


def base_context(request):
    root_page = getattr(Site.find_for_request(request), "root_page", None)
    pages = Page.objects.in_menu().child_of(root_page).specific()

    # filter menu items based on which pages the user can view
    def can_view(pages, usergroups):
        page_list = []
        for page in pages:
            subpages = page.get_children().in_menu().specific()
            if len(subpages) == 0:  # no subpages - add to list if visible
                is_matching_group = any(group in page.visible_for.all() for group in usergroups)
                if is_matching_group or page.is_public:
                    page_list.append(page)
            else:  # check subpages - add only if at least 1 subpage visible
                visible_subpages = can_view(subpages, usergroups)
                if len(visible_subpages) > 0:
                    page.menu_children = visible_subpages
                    page_list.append(page)
        return page_list

    usergroups = request.user.groups.all()
    if getattr(request.user, "_ip_range_group_name", None):
        usergroups = Group.objects.filter(
            Q(name=request.user._ip_range_group_name) | Q(id__in=request.user.groups.all())
        )

    shownPages = can_view(pages, usergroups)
    return {
        "root_page": root_page,
        "all_pages": shownPages if root_page else None,
    }
