from collections import defaultdict
from datetime import date

from django import forms
from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models import BooleanField, CharField, DateField, ForeignKey, Model, Q
from django.http import HttpResponseRedirect
from django_select2 import forms as s2forms
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import ItemBase, TagBase
from wagtail.admin.edit_handlers import FieldPanel, PublishingPanel
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.core.models import Page, Site
from wagtail.documents.models import Document
from wagtail.search import index

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.utils import get_user_groups
from myhpi.core.widgets import AttachmentSelectWidget


class BasePage(Page):
    visible_for = ParentalManyToManyField(Group, blank=True, related_name="visible_basepages")
    is_public = BooleanField()
    is_creatable = False

    settings_panels = [
        PublishingPanel(),
        FieldPanel("is_public", widget=forms.CheckboxInput),
        FieldPanel("visible_for", widget=forms.CheckboxSelectMultiple),
    ]
    # FilterFields required for restricting search results
    search_fields = Page.search_fields + [
        index.FilterField("group_id"),
        index.FilterField("is_public"),
    ]


class InformationPageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reinitialize widget
        self.fields["attachments"].widget = AttachmentSelectWidget(
            user=self.for_user, choices=self.fields["attachments"].widget.choices
        )


class InformationPage(BasePage):
    body = CustomMarkdownField()
    author_visible = BooleanField()
    attachments = ParentalManyToManyField(Document, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
        FieldPanel("attachments", widget=AttachmentSelectWidget),
    ]
    parent_page_types = [
        "FirstLevelMenuItem",
        "SecondLevelMenuItem",
        "InformationPage",
        "FooterCategory",
        "RootPage",
    ]
    settings_panels = [
        PublishingPanel(),
        FieldPanel("is_public", widget=forms.CheckboxInput),
        FieldPanel("visible_for", widget=forms.CheckboxSelectMultiple),
        FieldPanel("author_visible", widget=forms.CheckboxInput(attrs={"checked": ""})),
    ]
    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
    ]

    base_form_class = InformationPageForm

    @property
    def last_edited_by(self):
        if self.get_latest_revision():
            return self.get_latest_revision().user


class MinutesList(BasePage):
    group = ForeignKey(Group, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        FieldPanel("group", widget=forms.Select),
    ]
    parent_page_types = [
        "FirstLevelMenuItem",
        "SecondLevelMenuItem",
        "InformationPage",
        "FooterCategory",
        "RootPage",
    ]
    subpage_types = ["Minutes"]

    def get_visible_minutes(self, request):
        minutes_ids = self.get_children().exact_type(Minutes).values_list("id", flat=True)
        user_groups = get_user_groups(request.user)
        minutes_list = (
            Minutes.objects.filter(id__in=minutes_ids)
            .filter(Q(visible_for__in=user_groups) | Q(is_public=True))
            .order_by("-date")
            .distinct()
        )
        return minutes_list

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        minutes_list = self.get_visible_minutes(request)
        context.setdefault("minutes_list", minutes_list)
        minutes_by_years = defaultdict(lambda: [])
        for minute in minutes_list:
            minutes_by_years[minute.date.year].append(minute)
        context["minutes_by_years"] = dict(minutes_by_years)
        return context


class MinutesLabel(TagBase):
    free_tagging = False
    color = CharField(max_length=7, default="#000000")

    class Meta:
        verbose_name = "minutes label"
        verbose_name_plural = "minutes labels"


class TaggedMinutes(ItemBase):
    tag = models.ForeignKey(MinutesLabel, on_delete=models.CASCADE)
    content_object = ParentalKey(
        "core.Minutes", on_delete=models.CASCADE, related_name="tagged_items"
    )


class MinutesForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.minutes_list = kwargs["parent_page"]

        if not kwargs["instance"].title:  # Check if page has been created
            self.initial["date"] = date.today()
            self.initial["slug"] = date.today().isoformat()

            group = self.minutes_list.specific.group
            group_members = list(User.objects.filter(groups=group))
            self.initial["participants"] = group_members

            last_minutes = self.get_last_minutes()
            if last_minutes:
                self.initial["title"] = last_minutes.title
                self.initial["moderator"] = last_minutes.moderator
                self.initial["author"] = last_minutes.author

        self.fields["attachments"].widget = AttachmentSelectWidget(
            user=self.for_user, choices=self.fields["attachments"].widget.choices
        )

    def get_last_minutes(self):
        # Since the minutes aren't created yet, they are not yet in the tree
        existing_minutes = self.minutes_list.get_children().live()
        if existing_minutes:
            return existing_minutes.last().specific


class UserSelectWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "username__icontains",
        "email__icontains",
    ]


class Minutes(BasePage):
    date = DateField()
    moderator = ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="moderator"
    )
    author = ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="author"
    )
    participants = ParentalManyToManyField(User, related_name="minutes")
    labels = ClusterTaggableManager(through=TaggedMinutes, blank=True)
    text = CustomMarkdownField()
    guests = models.JSONField(blank=True, default=[])
    attachments = ParentalManyToManyField(Document, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("moderator"),
        FieldPanel("author"),
        FieldPanel("participants", widget=UserSelectWidget),
        FieldPanel("labels"),
        FieldPanel("text"),
        FieldPanel("guests"),
        FieldPanel("attachments", widget=AttachmentSelectWidget),
    ]
    parent_page_types = ["MinutesList"]
    subpage_types = []
    search_fields = BasePage.search_fields + [
        index.SearchField("text"),
        index.SearchField("participants"),
        index.SearchField("moderator"),
    ]

    base_form_class = MinutesForm


class RootPage(InformationPage):
    template = "core/information_page.html"

    parent_page_types = ["wagtailcore.Page"]


class FooterBase(BasePage):
    parent_page_types = ["RootPage"]
    subpage_types = [
        "FooterCategory",
    ]

    def serve(self, request, *args, **kwargs):
        # To handle the situation where someone inadvertently lands on a menu page, do a redirect
        first_descendant = self.get_descendants().first()
        if first_descendant:
            return HttpResponseRedirect(first_descendant.url)
        else:
            return HttpResponseRedirect(Site.find_for_request(request).root_page.url)


class FooterCategory(BasePage):
    parent_page_types = ["FooterBase"]
    subpage_types = ["InformationPage", "MinutesList", "RedirectMenuItem"]
    show_in_menus_default = True

    def serve(self, request, *args, **kwargs):
        # To handle the situation where someone inadvertently lands on a menu page, do a redirect
        first_descendant = self.get_descendants().first()
        if first_descendant:
            return HttpResponseRedirect(first_descendant.url)
        else:
            return HttpResponseRedirect(Site.find_for_request(request).root_page.url)


class FirstLevelMenuItem(BasePage):
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


class RedirectMenuItem(BasePage):
    parent_page_types = [
        "RootPage",
        "FooterCategory",
    ]
    subpage_types = []
    show_in_menus_default = True

    redirect_url = models.CharField(
        verbose_name="redirect URL",
        max_length=255,
        help_text="The URL that the user should be redirected to when selecting this menu item",
    )

    content_panels = BasePage.content_panels + [FieldPanel("redirect_url")]

    def serve(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=self.redirect_url)
