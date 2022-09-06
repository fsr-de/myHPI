from django import template

from myhpi.core.markdown.utils import render_markdown

register = template.Library()


@register.inclusion_tag("nav_level.html")
def build_nav_level(level_pages, level=0, parent_id="root"):
    return {"level_pages": level_pages, "level": level, "parent_id": parent_id}


@register.filter
def nav_children(page):
    return page.get_children().in_menu().live()


@register.filter(name="markdown")
def markdown(value):
    return render_markdown(value)
