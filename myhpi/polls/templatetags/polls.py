from django import template

register = template.Library()


@register.filter(name="can_vote")
def can_vote(poll, request):
    return poll.can_vote(request.user, request, allow_preview=True)
