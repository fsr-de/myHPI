import datetime

from django.contrib import messages
from django.db import models
from django.http import Http404
from django.template.response import TemplateResponse
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.edit_handlers import InlinePanel, FieldPanel
from wagtail.core.models import Page, Orderable
from django.contrib.auth.models import User

from myhpi.wagtail_markdown.edit_handlers import MarkdownPanel
from myhpi.wagtail_markdown.fields import MarkdownField


class Poll(Page):
    question = models.CharField(max_length=254)
    description = MarkdownField()
    start_date = models.DateField()
    end_date = models.DateField()

    participants = ParentalManyToManyField(User, related_name="polls")

    content_panels = Page.content_panels + [
        MarkdownPanel("description", classname="full"),
        FieldPanel('question'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
        InlinePanel('choices', label="Choices")
    ]
    # subpage_types = []

    def can_vote(self, user):
        return self.end_date > datetime.date.today() and user not in self.participants.all()

    def serve(self, request, *args, **kwargs):
        # has user permissions?
        if self.start_date > datetime.date.today():
            messages.warning(request, "This poll has not yet started.")
            # redirect to poll list page
        elif request.method == "POST":
            ...
            # handle vote
        else:
            return super().serve(request, *args, **kwargs)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["can_vote"] = self.can_vote(request.user)
        return context


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
    page = ParentalKey('polls.Poll', on_delete=models.CASCADE, related_name='choices')

    def percentage(self):
        participant_count = self.page.participants.count()
        if participant_count == 0:
            return 0
        return self.votes * 100 / participant_count