from django import template

register = template.Library()

@register.filter(name='can_vote')
def can_vote(poll, user):
    return poll.can_vote(user)
