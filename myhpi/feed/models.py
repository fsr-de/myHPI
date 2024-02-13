from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.markdown.utils import render_markdown
from myhpi.core.models import BasePage


class Feed(BasePage):
    parent_page_types = ["core.RootPage"]
    subpage_types = ["Post"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # TODO: Add pagination
        # Currently, there is no filter for visibility on posts. That is, it is assumed that all post should be visible to students
        context["posts"] = self.get_children().live().order_by("-first_published_at").specific()
        return context


class Post(BasePage):
    parent_page_types = ["Feed"]
    subpage_types = []
    body = CustomMarkdownField()
    post_account = models.ForeignKey(
        "PostAccount", related_name="posts", on_delete=models.SET_NULL, null=True, blank=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("body", classname="full"),
    ]

    @property
    def snippet(self):
        generated = render_markdown(self.body)
        length = 500
        if len(generated[0]) > length:
            return generated[0][:length] + "..."
        else:
            return generated[0]

    @property
    def author(self):
        if self.last_edited_by:
            return self.last_edited_by
        else:
            return self.post_account

    @property
    def date(self):
        return self.first_published_at.date()


# The PostAccount is used to create posts via API
@register_snippet
class PostAccount(models.Model):
    post_key = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
