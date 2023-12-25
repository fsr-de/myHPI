from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def next_minutes(context, minutes):
    all_minutes = list(minutes.get_parent().specific.get_visible_minutes(context.request))
    try:
        i = all_minutes.index(minutes)
        if i > 0:
            return all_minutes[i - 1]
    except ValueError:
        return


@register.simple_tag(takes_context=True)
def prev_minutes(context, minutes):
    all_minutes = list(minutes.get_parent().specific.get_visible_minutes(context.request))
    try:
        i = all_minutes.index(minutes)
        if i != len(all_minutes) - 1:
            return all_minutes[i + 1]
    except ValueError:
        return
