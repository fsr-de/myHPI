from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import DateField, ForeignKey, ManyToManyField
from django.http import HttpResponseRedirect
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page, Site
from wagtail_markdown.edit_handlers import MarkdownPanel
from wagtail_markdown.fields import MarkdownField


class InformationPage(Page):
    body = MarkdownField()

    content_panels = Page.content_panels + [
        MarkdownPanel('body', classname="full"),
    ]
    parent_page_types = ["FirstLevelMenuItem", "SecondLevelMenuItem", "InformationPage", "RootPage"]


class MinutesList(Page):
    group = ForeignKey(Group, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        FieldPanel("group"),
    ]
    parent_page_types = ["FirstLevelMenuItem", "SecondLevelMenuItem", "InformationPage", "RootPage"]
    subpage_types = ["Minutes"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        minutes_ids = self.get_children().exact_type(Minutes).values_list("id", flat=True)
        context.setdefault("minutes_list", Minutes.objects.filter(id__in=minutes_ids, group=self.group))
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
    subpage_types = []


class RootPage(InformationPage):
    template = "core/information_page.html"

    parent_page_types = ['wagtailcore.Page']


class FirstLevelMenuItem(Page):
    parent_page_types = ["RootPage"]
    subpage_types = ["SecondLevelMenuItem", "InformationPage", "MinutesList"]
    show_in_menus_default = True

    def serve(self, request, *args, **kwargs):
        # To handle the situation where someone inadvertently lands on a menu page, do a redirect
        first_descendant = self.get_descendants().first()
        if first_descendant:
            return HttpResponseRedirect(first_descendant.url)
        else:
            return HttpResponseRedirect(Site.find_for_request(request).root_page.url)


class SecondLevelMenuItem(FirstLevelMenuItem):
    parent_page_types = ["FirstLevelMenuItem"]
    subpage_types = ["InformationPage", "MinutesList"]
