from wagtail import hooks

from myhpi.polls.models import BasePoll, PollList


@hooks.register("before_serve_page")
def check_view_permissions(page, request, serve_args, serve_kwargs):
    if isinstance(page, (PollList, BasePoll)):
        page.specific.check_can_view(request)
