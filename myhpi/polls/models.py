import datetime
import heapq
import math

from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db import DatabaseError, IntegrityError, models, transaction
from django.db.models import F, Sum
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
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
        context.setdefault("poll_list", self.get_children().specific().live())
        return context


class BasePoll(BasePage):
    description = CustomMarkdownField()
    start_date = models.DateField()
    end_date = models.DateField()
    results_visible = models.BooleanField(default=False)
    eligible_groups = ParentalManyToManyField(Group, related_name="base_polls", blank=True)

    already_voted = models.ManyToManyField(User, related_name="base_polls")

    parent_page_types = [
        "PollList",
    ]
    subpage_types = []
    is_creatable = False

    def in_voting_period(self):
        return self.start_date <= datetime.date.today() <= self.end_date

    def can_vote(self, user):
        return (
            self.in_voting_period()
            and user not in self.already_voted.all()
            and self.eligible_groups.intersection(user.groups.all()).exists()
        )

    def cast_vote(self, request, *args, **kwargs):
        raise NotImplemented()

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            if self.can_vote(request.user):
                return self.cast_vote(request, *args, **kwargs)
            messages.error(request, _("You are not allowed to vote."))
        return super().serve(request, *args, **kwargs)


class MajorityVotePoll(BasePoll):
    question = models.CharField(max_length=254)
    max_allowed_answers = models.IntegerField(default=1)

    content_panels = Page.content_panels + [
        FieldPanel("description", classname="full"),
        FieldPanel("question"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("eligible_groups"),
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
            messages.error(request, _("You must select at least one choice."))
        elif len(choices) > self.max_allowed_answers:
            messages.error(
                request,
                _("You can only select up to {} options.").format(self.max_allowed_answers),
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
                    messages.error(request, _("Invalid choice."))
            if confirmed_choices > 0:
                self.already_voted.add(request.user)
                messages.success(request, _("Your vote has been counted."))
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
        FieldPanel("eligible_groups"),
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
        form = self.get_ballot_form(request.POST)
        if not form.is_valid():
            messages.error(
                request,
                mark_safe(
                    _("Invalid ballot.\n{errors}").format(
                        errors=", ".join([str(err) for err in form.errors.values()])
                    )
                ),
            )
        else:
            try:
                qs = RankedChoicePoll.objects.select_for_update().filter(pk=self.pk)
                with transaction.atomic():
                    # acquire lock for this transaction by evaluating the queryset
                    date = qs.get().start_date
                    if self.already_voted.filter(pk=request.user.pk).exists():
                        messages.error(request, _("You have already voted."))
                    else:
                        ballot = RankedChoiceBallot.objects.create(poll=self)
                        for option in self.options.all():
                            if f"option_{option.pk}" in form.cleaned_data:
                                entry = RankedChoiceBallotEntry.objects.create(
                                    ballot=ballot,
                                    option=option,
                                    rank=form.cleaned_data[f"option_{option.pk}"],
                                )
                                entry.save()
                        self.already_voted.add(request.user)
                        messages.success(request, _("Your vote has been counted."))
            except IntegrityError:
                messages.error(request, _("Invalid ballot."))
            except DatabaseError:
                messages.error(request, _("A database error occured. Please try again."))
        return redirect(self.relative_url(self.get_site()))

    def get_ballot_form(self, data=None):
        from myhpi.polls.forms import RankedChoiceBallotForm

        return RankedChoiceBallotForm(data, options=self.options.all())

    def __str__(self):
        return self.title

    @staticmethod
    def _heapify_ballot(ballot):
        result = []
        for entry in ballot.rankedchoiceballotentry_set.all():
            result.append((entry.rank, entry))
        heapq.heapify(result)
        return result

    def calculate_ranking(self):
        ballots = list(
            map(
                lambda x: self._heapify_ballot(x),
                list(self.ballots.prefetch_related("rankedchoiceballotentry_set__option")),
            )
        )
        options = self.options.all()

        total_votes = len(ballots)

        current_votes = {}
        names = {}

        for option in options:
            current_votes[option.pk] = []
            names[option.pk] = option.name

        for ballot in ballots:
            current_votes[heapq.heappop(ballot)[1].option.pk].append(ballot)

        def find_loosers():
            threshold = min(map(lambda key: len(current_votes[key]), current_votes.keys()))
            return set(
                filter(lambda key: len(current_votes[key]) == threshold, current_votes.keys())
            )

        final_votes = {}

        while current_votes:
            loosers = find_loosers()

            for looser in loosers:
                final_votes[looser] = len(current_votes[looser])

            for looser in loosers:
                for ballot in current_votes.pop(looser, []):
                    while True:
                        if not ballot:
                            break
                        next_option = heapq.heappop(ballot)[1].option.pk
                        if not next_option in loosers and next_option in current_votes.keys():
                            current_votes[next_option].append(ballot)
                            break

        sorted_votes = sorted(
            map(lambda tuple: (tuple[1], tuple[0]), final_votes.items()), reverse=True
        )
        assigned_rank = 0
        rank = 0
        previous_votes = None
        results = []
        for candidate in sorted_votes:
            rank += 1
            if previous_votes is None or previous_votes > candidate[0]:
                assigned_rank = rank
            results.append((assigned_rank, names[candidate[1]], candidate[0]))
            previous_votes = candidate[0]

        return sorted(results)


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

    def __str__(self):
        return ", ".join(map(lambda x: str(x), self.entries.all()))


class RankedChoiceBallotEntry(models.Model):
    ballot = models.ForeignKey(RankedChoiceBallot, on_delete=models.CASCADE)
    option = models.ForeignKey(RankedChoiceOption, on_delete=models.CASCADE)
    rank = models.IntegerField()

    class Meta:
        unique_together = [["ballot", "option"], ["ballot", "rank"]]

    def __str__(self):
        return f"{self.option} on rank {self.rank}"


def heappeek(heap):
    return heap[0][1]
