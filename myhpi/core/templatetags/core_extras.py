import re

from django import template
from django.template import Context, Template

from myhpi import settings
from myhpi.core.markdown.utils import render_markdown
from myhpi.core.models import Footer

register = template.Library()


@register.inclusion_tag("nav_level.html")
def build_nav_level(level_pages, level=0, parent_id="root"):
    return {"level_pages": level_pages, "level": level, "parent_id": parent_id}


@register.filter
def nav_children(page):
    return page.get_children().in_menu().live()


@register.inclusion_tag("footer.html")
def insert_footer():
    footer = Footer.objects.first()
    return {"footer_columns": [footer.column_1, footer.column_2, footer.column_3, footer.column_4]}


@register.filter(name="tag_external_links")
def tag_external_links(content):
    """Takes the content of a website and inserts external link icons after every external link."""
    external_links = re.finditer('<a[^>]*href="(?!' + settings.SITE_URL + ")[^>]*>[^<]*", content)
    for link in reversed(list(external_links)):
        content = (
            content[: link.end()]
            + " {% bs_icon 'box-arrow-up-right' extra_classes='external-link-icon' %}"
            + content[link.end() :]
        )
    template = Template("{% load bootstrap_icons %}" + content)
    return template.render(Context())


@register.filter(name="markdown")
def markdown(value):
    return render_markdown(value)
