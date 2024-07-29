from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.template.response import TemplateResponse
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page

from myhpi.core.models import BasePage
from myhpi.core.utils import get_user_groups


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        user_groups = get_user_groups(request.user)
        allowed_pages = (
            BasePage.objects.live()
            .filter(Q(visible_for__in=user_groups) | Q(is_public=True))
            .distinct()
            .order_by("-last_published_at")
        )
        search_results = allowed_pages.search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 20)
    try:
        search_results_page = paginator.page(page)
    except PageNotAnInteger:
        search_results_page = paginator.page(1)
    except EmptyPage:
        search_results_page = paginator.page(paginator.num_pages)

    return TemplateResponse(
        request,
        "search/search.html",
        {
            "search_query": search_query,
            "search_results_page": search_results_page,
        },
    )
