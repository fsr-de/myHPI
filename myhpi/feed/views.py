import datetime
import json

from django.http import HttpResponse
from django.views import View

from myhpi.feed.models import Feed, Post, PostAccount


class PostFeedEntryView(View):
    def post(self, request, *args, **kwargs):
        provided_key = request.headers.get("X-API-KEY")
        post_account = PostAccount.objects.filter(post_key=provided_key).first()
        if not post_account:
            return HttpResponse("Unauthorized", status=401)
        else:
            feed = Feed.objects.first()
            if not feed:
                return HttpResponse("No feed found", status=500)

            # Parse body as JSON
            body = json.loads(request.body)

            feed.add_child(
                instance=Post(
                    title=body["title"],
                    body=body["body"],
                    owner=None,
                    is_public=False,
                    post_account=post_account,
                    first_published_at=datetime.datetime.now(datetime.UTC),
                )
            )
            return HttpResponse("OK", status=200)
