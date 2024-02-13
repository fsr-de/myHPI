import re

from django import template
from django.template import Context, Template

from myhpi import settings
from myhpi.core.markdown.utils import render_markdown
from myhpi.core.models import Footer

register = template.Library()


@register.inclusion_tag("nav_level.html", takes_context=True)
def build_nav_level_for(context, parent_page, level=0, parent_id="root"):
    return {
        "level_pages": context["pages_by_parent"][
            parent_page.path
        ],  # all pages to display on this level
        "level": level,
        "parent_id": parent_id,
        "pages_by_parent": context[
            "pages_by_parent"
        ],  # lookup by parent page for all pages visible for the user
    }


@register.filter()
def get_nav_children_for(pages_by_parent, parent_path):
    return pages_by_parent[parent_path]


@register.inclusion_tag("footer.html")
def insert_footer(page):
    footer = Footer.objects.first()
    return {"footer_columns": [footer.column_1, footer.column_2, footer.column_3], "page": page}


@register.filter(name="tag_external_links")
def tag_external_links(content):
    """Takes the content of a website and inserts external link icons after every external link."""
    external_links = re.finditer(
        '<a[^>]*href="(?!' + settings.SITE_URL + ")(?!\/)[^>]*>[^<]*", content
    )
    for link in reversed(list(external_links)):
        content = (
            content[: link.start() + 2]
            + " target='_blank'"
            + content[link.start() + 2 : link.end()]
            + " {% bs_icon 'box-arrow-up-right' extra_classes='external-link-icon' %}"
            + content[link.end() :]
        )
    template = Template("{% load bootstrap_icons %}" + content)
    return template.render(Context())


@register.filter(name="touchify_abbrevations")
def touchify_abbrevations(content):
    """Takes the content of a website and inserts external link icons after every external link."""
    external_links = re.finditer('<abbr[^>]*>[^<]*', content)
    for link in reversed(list(external_links)):
        content = (
            content[: link.start() + 5]
            + " tabindex=0"
            + content[link.start() + 5 :]
        )
    template = Template("{% load bootstrap_icons %}" + content)
    return template.render(Context())


@register.filter(name="markdown")
def markdown(value):
    return render_markdown(value)


@register.filter(name="get_link_for_group")
def get_link_for_group(minutes_creation_links, group):
    return minutes_creation_links[group.id]
