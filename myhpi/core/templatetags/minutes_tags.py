from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def next_minutes(context, minutes):
    # This may be None if there is no next minutes.
    return (
        minutes.get_parent()
        .specific.get_visible_minutes(context.request)
        .exclude(basepage_ptr_id__lte=minutes.basepage_ptr_id, date=minutes.date)
        .filter(date__gte=minutes.date)
        .order_by("date", "basepage_ptr_id")
    ).first()


@register.simple_tag(takes_context=True)
def prev_minutes(context, minutes):
    # This may be None if there is no previous minutes.
    return (
        minutes.get_parent()
        .specific.get_visible_minutes(context.request)
        .exclude(basepage_ptr_id__gte=minutes.basepage_ptr_id, date=minutes.date)
        .filter(date__lte=minutes.date)
        .order_by("-date", "-basepage_ptr_id")
    ).first()
