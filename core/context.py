from wagtail.core.models import Page, Site


def base_context(request):
    root_page = getattr(Site.find_for_request(request), "root_page", None)
    return {
        "root_page": root_page,
        "all_pages": Page.objects.in_menu().child_of(root_page),
    }
