from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import DateField, ForeignKey, ManyToManyField, Model, CharField
from django.http import HttpResponseRedirect
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase, TagBase, ItemBase
from wagtail.admin.edit_handlers import FieldPanel, PublishingPanel
from wagtail.core.models import Page, Site
from wagtail.snippets.models import register_snippet

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


class MinutesLabel(TagBase):
    free_tagging = False

    class Meta:
        verbose_name = "minutes label"
        verbose_name_plural = "minutes labels"


class TaggedMinutes(ItemBase):
    tag = models.ForeignKey(MinutesLabel, on_delete=models.CASCADE)
    content_object = ParentalKey('core.Minutes', on_delete=models.CASCADE, related_name='tagged_items')


class Minutes(Page):
    group = ForeignKey(Group, on_delete=models.PROTECT, null=True)
    date = DateField()
    moderator = ForeignKey(User, on_delete=models.CASCADE, related_name="moderator")
    author = ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    participants = ParentalManyToManyField(User, related_name="participants")
    labels = ClusterTaggableManager(through=TaggedMinutes, blank=True)
    visible_for = ParentalManyToManyField(Group, related_name="visible_for")
    text = MarkdownField()

    content_panels = Page.content_panels + [
        FieldPanel("group"),
        FieldPanel("date"),
        FieldPanel("moderator"),
        FieldPanel("author"),
        FieldPanel("participants"),
        FieldPanel("labels"),
        MarkdownPanel('text', classname="full"),
    ]
    settings_panels = [
        PublishingPanel(),
        FieldPanel("visible_for"),
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


class AbbreviationExplanation(Model):
    abbreviation = CharField(max_length=255)
    explanation = CharField(max_length=255)

    def __str__(self):
        return self.abbreviation