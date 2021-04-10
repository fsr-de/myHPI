from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import DateField, ForeignKey, ManyToManyField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail_markdown.edit_handlers import MarkdownPanel
from wagtail_markdown.fields import MarkdownField


class InformationPage(Page):
    body = MarkdownField()

    content_panels = Page.content_panels + [
        MarkdownPanel('body', classname="full"),
    ]


class MinutesList(Page):
    group = ForeignKey(Group, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        FieldPanel("group"),
    ]
    subpage_types = ["Minutes"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.setdefault("minutes_list", Minutes.objects.live().filter(group=self.group))
        return context


class Minutes(Page):
    group = ForeignKey(Group, on_delete=models.PROTECT, null=True)
    date = DateField()
    moderator = ForeignKey(User, on_delete=models.CASCADE, related_name="moderator")
    author = ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    participants = ManyToManyField(User, related_name="participants")
    text = MarkdownField()

    content_panels = Page.content_panels + [
        FieldPanel("group"),
        FieldPanel("date"),
        FieldPanel("moderator"),
        FieldPanel("author"),
        FieldPanel("participants"),
        MarkdownPanel('text', classname="full"),
    ]
    parent_page_types = ["MinutesList"]
