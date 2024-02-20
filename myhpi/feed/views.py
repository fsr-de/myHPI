import datetime
import json

from django.core.exceptions import MultipleObjectsReturned, SuspiciousOperation
from django.http import HttpResponse
from django.views import View

from myhpi.feed.models import NewsFeed, NewsFeedAccount, Post


class PostFeedEntryView(View):
    def post(self, request, *args, **kwargs):
        provided_key = request.headers.get("X-API-KEY")
        post_accounts = NewsFeedAccount.objects.filter(post_key=provided_key)
        if post_accounts.count() == 0:
            return HttpResponse("Unauthorized", status=401)
        if post_accounts.count() > 1:
            raise MultipleObjectsReturned("Multiple post accounts with the same key found")
        else:
            post_account = post_accounts.first()
            feed = NewsFeed.objects.first()
            if not feed:
                return HttpResponse("No feed found", status=500)

            # Parse body as JSON
            body = json.loads(request.body)

            post = feed.add_child(
                instance=Post(
                    title=body["title"],
                    body=body["body"],
                    owner=None,
                    is_public=False,
                    post_account=post_account,
                    first_published_at=datetime.datetime.now(datetime.UTC),
                )
            )
            return HttpResponse(post.id, status=200)
