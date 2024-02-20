from django.core.paginator import Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.users.models import UserProfile, upload_avatar_to

from myhpi import settings
from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.models import BasePage


class NewsFeed(BasePage):
    parent_page_types = ["core.RootPage"]
    subpage_types = ["Post"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_posts = self.get_children().live().order_by("-first_published_at").specific()
        paginator = Paginator(all_posts, 10)
        page = paginator.get_page(request.GET.get("page"))

        # Currently, there is no filter for visibility on posts. That is, it is assumed that all post should be visible to students
        context["page"] = page
        context["posts"] = page.object_list
        context["limit"] = settings.FEED_TRUNCATE_LIMIT
        return context


class Post(BasePage):
    parent_page_types = ["NewsFeed"]
    subpage_types = []
    body = CustomMarkdownField()
    post_account = models.ForeignKey(
        "NewsFeedAccount", related_name="posts", on_delete=models.SET_NULL, null=True, blank=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("body", classname="full"),
    ]

    @property
    def author(self):
        if self.last_edited_by:
            return self.last_edited_by
        else:
            return self.post_account

    @property
    def date(self):
        return self.first_published_at.date()

    @property
    def image_url(self):
        if self.post_account and self.post_account.icon:
            return self.post_account.icon.url
        # user = self.author if self.author else self.owner
        # if user:
        #    profile = UserProfile.get_for_user(user)
        #    return profile.avatar.url
        else:
            return "https://www.gravatar.com/avatar/b1a83a1baa8a1d45c905a59217a7d30a?s=140&d=mm"


# The NewsFeedAccount is used to create posts via API
@register_snippet
class NewsFeedAccount(models.Model):
    post_key = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    icon = models.ImageField(upload_to=upload_avatar_to, null=True, blank=True)

    def __str__(self):
        return self.name
