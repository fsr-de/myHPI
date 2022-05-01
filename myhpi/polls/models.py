import datetime

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum
from django.shortcuts import redirect
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.core.models import Orderable, Page

from myhpi.wagtail_markdown.edit_handlers import MarkdownPanel
from myhpi.wagtail_markdown.fields import MarkdownField


class PollList(Page):
    parent_page_types = [
        "core.RootPage",
    ]
    subpage_types = ["Poll"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.setdefault("poll_list", self.get_children().exact_type(Poll))
        return context


class Poll(Page):
    question = models.CharField(max_length=254)
    description = MarkdownField()
    start_date = models.DateField()
    end_date = models.DateField()
    max_allowed_answers = models.IntegerField(default=1)
    results_visible = models.BooleanField(default=False)

    participants = models.ManyToManyField(User, related_name="polls")

    content_panels = Page.content_panels + [
        MarkdownPanel("description", classname="full"),
        FieldPanel("question"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("max_allowed_answers"),
        FieldPanel("results_visible"),
        InlinePanel("choices", label="Choices"),
    ]
    parent_page_types = [
        "PollList",
    ]
    subpage_types = []

    def can_vote(self, user):
        return self.end_date > datetime.date.today() and user not in self.participants.all()

    def serve(self, request, *args, **kwargs):
        if self.start_date > datetime.date.today():
            messages.warning(request, "This poll has not yet started.")
            return redirect(self.get_parent().relative_url(self.get_site()))
        elif request.method == "POST" and self.can_vote(request.user):
            choices = request.POST.getlist("choice")
            if len(choices) == 0:
                messages.error(request, "You must at least select one choice.")
            elif len(choices) > self.max_allowed_answers:
                messages.error(
                    request,
                    "You can only select up to {} options.".format(self.max_allowed_answers),
                )
            else:
                for choice_id in choices:
                    choice = self.choices.filter(id=choice_id)
                    choice.update(votes=F("votes") + 1)
                self.participants.add(request.user)
                messages.success(request, "Your vote has been counted.")
                return redirect(self.relative_url(self.get_site()))

        return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["can_vote"] = self.can_vote(request.user)
        return context

    @property
    def num_votes(self):
        return self.choices.aggregate(Sum("votes")).get("votes__sum")


class Choice(models.Model):
    text = models.CharField(max_length=254)
    votes = models.IntegerField(default=0)

    panels = [
        FieldPanel("text"),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        return self.text


class PollChoice(Orderable, Choice):
    page = ParentalKey("polls.Poll", on_delete=models.CASCADE, related_name="choices")

    def percentage(self):
        participant_count = self.page.participants.count()
        if participant_count == 0:
            return 0
        return self.votes * 100 / participant_count
