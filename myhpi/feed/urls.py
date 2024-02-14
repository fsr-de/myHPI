from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from myhpi.feed.views import PostFeedEntryView

urlpatterns = [path("createPost", csrf_exempt(PostFeedEntryView.as_view()), name="post-feed-entry")]