from datetime import date

from django import forms
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import BooleanField, CharField, DateField, ForeignKey, Model, Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django_select2 import forms as s2forms
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import ItemBase, TagBase
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, PublishingPanel
from wagtail.documents.models import Document
from wagtail.models import Page, Site, TranslatableMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import SynchronizedField

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.utils import get_user_groups
from myhpi.core.widgets import AttachmentSelectWidget, TextArrayWidget


class BasePage(Page):
    visible_for = ParentalManyToManyField(Group, blank=True, related_name="visible_basepages")
    is_public = BooleanField()
    is_creatable = False

    override_translatable_fields = [
        SynchronizedField("visible_for"),
    ]
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

    def check_can_view(self, request):
        target_groups = request.user.groups.all()
        if request.user.is_superuser:
            return
        if getattr(request.user, "ip_range_group_name", None):
            target_groups = Group.objects.filter(
                Q(name=request.user.ip_range_group_name) | Q(id__in=request.user.groups.all())
            )
        is_matching_group = any(group in self.visible_for.all() for group in target_groups)
        if not (is_matching_group or self.is_public):
            raise PermissionDenied


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

    override_translatable_fields = [
        SynchronizedField("attachments"),
    ]
    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
        FieldPanel("attachments", widget=AttachmentSelectWidget),
    ]
    parent_page_types = [
        "MenuItem",
        "InformationPage",
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
            user = self.get_latest_revision().user
            return f"{user.first_name} {user.last_name}"


class MinutesList(BasePage):
    group = ForeignKey(Group, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        FieldPanel("group", widget=forms.Select),
    ]
    parent_page_types = [
        "MenuItem",
        "InformationPage",
        "RootPage",
    ]
    subpage_types = ["Minutes"]

    def get_visible_minutes(self, request):
        user_groups = get_user_groups(request.user)
        minutes = Minutes.objects.child_of(self)

        visible_minutes = minutes.filter(Q(visible_for__in=user_groups) | Q(is_public=True))
        # display all minutes including drafts if user is in group that owns the minutes list
        if self.group in user_groups:
            visible_minutes = minutes
        return visible_minutes

    def get_visible_minutes_for_year(self, request):
        visible_minutes = self.get_visible_minutes(request)
        try:
            year = request.GET.get("year", None)
            if year is None:
                year = visible_minutes.order_by("-date")[0].date.year
            else:
                year = int(year)
        except (ValueError, IndexError):
            year = date.today().year
        year_list = list(map(lambda d: d.year, visible_minutes.dates("date", "year")))

        minutes = visible_minutes.filter(date__year=year).order_by("-date").distinct()
        return year, year_list, minutes

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        selected_year, all_years, minutes = self.get_visible_minutes_for_year(request)
        context["selected_year"], context["all_years"] = selected_year, all_years
        try:
            year_index = all_years.index(selected_year)
            context["year_range"] = all_years[max(year_index - 3, 0) : year_index + 4]
        except ValueError:
            context["year_range"] = all_years[-3:]
        context["minutes"], context["minutes_list"] = minutes, self
        return context


@register_snippet
class MinutesLabel(TagBase):
    free_tagging = False
    color = CharField(max_length=7, default="#000000")

    class Meta:
        verbose_name = "minutes label"
        verbose_name_plural = "minutes labels"


class TaggedMinutes(ItemBase):
    tag = models.ForeignKey(
        MinutesLabel, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_items"
    )
    content_object = ParentalKey(
        "core.Minutes", on_delete=models.CASCADE, related_name="tagged_items"
    )


class MinutesForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not kwargs["instance"].title:  # Check if page has been created
            self.minutes_list = kwargs["parent_page"]

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
        self.fields["guests"].widget = TextArrayWidget()

    def get_last_minutes(self):
        # Since the minutes aren't created yet, they are not yet in the tree
        existing_minutes = self.minutes_list.get_children().live()
        if existing_minutes:
            return existing_minutes.last().specific


class UserSelectMultipleWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "username__icontains",
        "email__icontains",
        "first_name__icontains",
        "last_name__icontains",
    ]

    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserSelectWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "username__icontains",
        "email__icontains",
        "first_name__icontains",
        "last_name__icontains",
    ]

    def label_from_instance(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class Minutes(BasePage):
    date = DateField()
    moderator = ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="moderator"
    )
    author = ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="author"
    )
    participants = ParentalManyToManyField(User, related_name="minutes")
    location = CharField(max_length=255, blank=True)
    labels = ClusterTaggableManager(through=TaggedMinutes, blank=True)
    body = CustomMarkdownField()
    guests = models.JSONField(blank=True, default=[])
    attachments = ParentalManyToManyField(Document, blank=True)

    override_translatable_fields = [
        SynchronizedField("participants"),
        SynchronizedField("attachments"),
    ]
    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("moderator", widget=UserSelectWidget({"data-width": "100%"})),
        FieldPanel("author", widget=UserSelectWidget({"data-width": "100%"})),
        FieldPanel("participants", widget=UserSelectMultipleWidget({"data-width": "100%"})),
        FieldPanel("location"),
        FieldPanel("labels"),
        FieldPanel("body"),
        FieldPanel("guests"),
        FieldPanel("attachments", widget=AttachmentSelectWidget),
    ]
    parent_page_types = ["MinutesList"]
    subpage_types = []
    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
        index.SearchField("participants"),
        index.SearchField("moderator"),
    ]

    base_form_class = MinutesForm

    # this function also fetches the correct draft url if the minute is still a draft
    def get_valid_url(self):
        return (
            self.url
            if self.live
            else reverse("wagtailadmin_pages:view_draft", kwargs={"page_id": self.id})
        )


class RootPage(InformationPage):
    template = "core/information_page.html"

    parent_page_types = ["wagtailcore.Page"]


@register_snippet
class Footer(models.Model):
    column_1 = CustomMarkdownField()
    column_2 = CustomMarkdownField()
    column_3 = CustomMarkdownField()

    panels = [
        FieldPanel("column_1"),
        FieldPanel("column_2"),
        FieldPanel("column_3"),
    ]

    def __str__(self):
        def get_first_line(content):
            return content.split("\n", 1)[0]

        return (
            get_first_line(self.column_1)
            + get_first_line(self.column_2)
            + get_first_line(self.column_3)
        )


class MenuItem(BasePage):
    parent_page_types = ["RootPage", "MenuItem"]
    subpage_types = ["MenuItem", "InformationPage", "MinutesList"]
    preview_modes = []
    show_in_menus_default = True

    def serve(self, request, *args, **kwargs):
        # To handle the situation where someone inadvertently lands on a menu page, do a redirect
        first_descendant = self.get_descendants().first()
        if first_descendant:
            return HttpResponseRedirect(first_descendant.url)
        else:
            return HttpResponseRedirect(Site.find_for_request(request).root_page.url)


@register_snippet
class AbbreviationExplanation(TranslatableMixin, Model):
    abbreviation = CharField(max_length=255)
    explanation = CharField(max_length=255)

    def __str__(self):
        return f"{self.abbreviation}: {self.explanation}"

    override_translatable_fields = [SynchronizedField("abbreviation", overridable=False)]


class RedirectMenuItem(BasePage):
    parent_page_types = [
        "RootPage",
    ]
    subpage_types = []
    preview_modes = []
    show_in_menus_default = True

    redirect_url = models.CharField(
        verbose_name="redirect URL",
        max_length=255,
        help_text="The URL that the user should be redirected to when selecting this menu item",
    )

    content_panels = BasePage.content_panels + [FieldPanel("redirect_url")]

    def serve(self, request, *args, **kwargs):
        return HttpResponseRedirect(redirect_to=self.redirect_url)
