from django.http import HttpResponseRedirect

from myhpi import settings
from myhpi.feed.models import NewsFeed


class FeedRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.feed = NewsFeed.objects.first()

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        user = request.user
        if (
            self.feed
            and request.path == "/"
            and user.is_authenticated
            and self.feed.visible_for.intersection(user.groups.all()).exists()
            and request.GET.get("no_redirect") != "true"
            and settings.REDIRECT_TO_FEED
        ):
            request.path = self.feed.slug
