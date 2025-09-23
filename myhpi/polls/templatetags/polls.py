from django import template
from wagtail.models import Locale

register = template.Library()


@register.filter(name="can_vote")
def can_vote(poll, request):
    return poll.can_vote(request.user, request, allow_preview=True)


@register.filter
def get_localized_choice(canonical_choice, request):
    locale_code = request.LANGUAGE_CODE
    locale = Locale.objects.get(language_code=locale_code)
    localized_choice = canonical_choice.get_translation_or_none(locale)
    if localized_choice:
        return localized_choice


# Ranked choice poll localization utilities


@register.filter
def get_localized_form(canonical_poll, request):
    locale_code = request.LANGUAGE_CODE
    locale = Locale.objects.get(language_code=locale_code)
    return canonical_poll.get_ballot_form(locale=locale)


@register.filter
def get_localized_results(canonical_poll, request):
    locale_code = request.LANGUAGE_CODE
    locale = Locale.objects.get(language_code=locale_code)
    return canonical_poll.calculate_ranking(locale=locale)
