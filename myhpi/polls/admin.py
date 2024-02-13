from django.contrib import admin

from myhpi.polls.models import (
    RankedChoiceBallot,
    RankedChoiceBallotEntry,
    RankedChoiceOption,
    RankedChoicePoll,
)

admin.site.register(RankedChoiceBallot)
admin.site.register(RankedChoiceBallotEntry)
admin.site.register(RankedChoiceOption)
admin.site.register(RankedChoicePoll)
