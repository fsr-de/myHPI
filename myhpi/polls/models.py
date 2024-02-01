import datetime
import queue
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable, Page
from wagtail.search import index

from myhpi.core.markdown.fields import CustomMarkdownField
from myhpi.core.models import BasePage


class PollList(BasePage):
    parent_page_types = [
        "core.RootPage",
    ]
    subpage_types = ["MajorityVotePoll", "RankedChoicePoll"]
    max_count = 1

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.setdefault(
            "poll_list",
            self.get_children().specific().live()
        )
        return context


class BasePoll(BasePage):
    description = CustomMarkdownField()
    start_date = models.DateField()
    end_date = models.DateField()
    results_visible = models.BooleanField(default=False)

    already_voted = models.ManyToManyField(User, related_name="base_polls")

    parent_page_types = [
        "PollList",
    ]
    subpage_types = []
    is_creatable = False

    def in_voting_period(self):
        return self.start_date <= datetime.date.today() <= self.end_date

    def can_vote(self, user):
        return self.in_voting_period() and user not in self.already_voted.all()

    def cast_vote(self, request, *args, **kwargs):
        raise NotImplemented()

    def serve(self, request, *args, **kwargs):
        if request.method == "POST" and self.can_vote(request.user):
            self.cast_vote(request, *args, **kwargs)
        return super().serve(request, *args, **kwargs)


class MajorityVotePoll(BasePoll):
    question = models.CharField(max_length=254)
    max_allowed_answers = models.IntegerField(default=1)

    content_panels = Page.content_panels + [
        FieldPanel("description", classname="full"),
        FieldPanel("question"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("max_allowed_answers"),
        FieldPanel("results_visible"),
        InlinePanel("choices", label="Choices"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("description"),
        index.SearchField("question"),
    ]

    is_creatable = True

    def cast_vote(self, request, *args, **kwargs):
        choices = request.POST.getlist("choice")
        if len(choices) == 0:
            messages.error(request, "You must select at least one choice.")
        elif len(choices) > self.max_allowed_answers:
            messages.error(
                request,
                "You can only select up to {} options.".format(self.max_allowed_answers),
            )
        else:
            confirmed_choices = 0
            for choice_id in choices:
                choice = self.choices.filter(id=choice_id).first()
                if choice and choice.page == self:
                    choice.votes += 1
                    choice.save()
                    confirmed_choices += 1
                else:
                    messages.error(request, "Invalid choice.")
            if confirmed_choices > 0:
                self.already_voted.add(request.user)
                messages.success(request, "Your vote has been counted.")
            return redirect(self.relative_url(self.get_site()))

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["can_vote"] = self.can_vote(request.user)
        return context

    @property
    def num_votes(self):
        return self.choices.aggregate(Sum("votes")).get("votes__sum")


class MajorityVoteChoice(Orderable):
    text = models.CharField(max_length=254)
    votes = models.IntegerField(default=0)
    page = ParentalKey("MajorityVotePoll", on_delete=models.CASCADE, related_name="choices")

    panels = [
        FieldPanel("text"),
    ]

    def __str__(self):
        return self.text

    def percentage(self):
        participant_count = self.page.already_voted.count()
        if participant_count == 0:
            return 0
        return self.votes * 100 / participant_count


class RankedChoicePoll(BasePoll):
    content_panels = Page.content_panels + [
        FieldPanel("description", classname="full"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("results_visible"),
        InlinePanel("options", label="Options"),
    ]

    parent_page_types = [
        "PollList",
    ]
    subpage_types = []
    search_fields = BasePage.search_fields + [
        index.SearchField("description"),
    ]

    is_creatable = True

    def cast_vote(self, request, *args, **kwargs):
        print(f"Cast vote: {request}")
        return True

    def calculate_ranking(self):
        ballots = map(lambda x: x.as_sensible_datastructure(), self.ballots.all())
        options = self.options.all()

        current_votes = {}
        active_options = len(options)

        for option in options:
            current_votes[option.pk] = 0

        return [(1, "Julian", 100)]



class RankedChoiceOption(Orderable):
    name = models.CharField(max_length=254)
    description = CustomMarkdownField()
    poll = ParentalKey("RankedChoicePoll", related_name="options")

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
    ]

    def __str__(self):
        return self.name


class RankedChoiceBallot(models.Model):
    poll = models.ForeignKey(RankedChoicePoll, on_delete=models.CASCADE, related_name="ballots")
    entries = models.ManyToManyField(RankedChoiceOption, through="RankedChoiceBallotEntry")

    def as_sensible_datastructure(self):
        result = queue.PriorityQueue()
        for entry in self.entries:
            result.put((entry.rank, entry.option))
        return result

    def __str__(self):
        ", ".join(map(lambda x: str(x), self.entries.all()))


class RankedChoiceBallotEntry(models.Model):
    ballot = models.ForeignKey(RankedChoiceBallot, on_delete=models.CASCADE)
    option = models.ForeignKey(RankedChoiceOption, on_delete=models.CASCADE)
    rank = models.IntegerField()

    class Meta:
        unique_together = [["ballot", "option"], ["ballot", "rank"]]
