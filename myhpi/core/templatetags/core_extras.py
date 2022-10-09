from django import template

from myhpi.core.markdown.utils import render_markdown

register = template.Library()


@register.inclusion_tag("nav_level.html")
def build_nav_level(level_pages, level=0, parent_id="root"):
    return {"level_pages": level_pages, "level": level, "parent_id": parent_id}


@register.filter
def nav_children(page):
    return page.get_children().in_menu().live()


@register.inclusion_tag("footer.html")
def build_footer(footer_base):
    return {"footer_base": footer_base}


@register.filter
def footer_children(footer_page):
    if footer_page is None:
        return []
    return footer_page.get_children().in_menu().live()


@register.inclusion_tag("link.html")
def insert_link(page):
    return {"page": page}


@register.filter
def is_external_url(page):
    return hasattr(page.specific, "redirect_url")


@register.filter
def actual_url(page):
    return page.specific.redirect_url if is_external_url(page) else page.url


@register.filter(name="markdown")
def markdown(value):
    return render_markdown(value)
