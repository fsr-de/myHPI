import re

from django import template
from django.template import Context, Template

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


@register.filter()
def hasTocContent(toc):
    return "li" in toc


@register.filter(name="tag_external_links")
def tag_external_links(content):
    """Takes the content of a website and inserts external link icons after every external link."""
    external_links = re.finditer(
        # Matches any <a> tags (and any tags inside it) which href does not start with # (anchors) or /a (relative to site root).
        # The SITE_URL is not included in internal links inserted via the editor: [Home](page:3) => <a href="/en/">Home</a>
        r'<a[^>]*href="(?!#|/\w)[^>]*>(.*?)</a>',
        content,
    )
    for link in reversed(list(external_links)):
        content = (
            content[: link.start() + len("<a")]
            + " target='_blank'"
            + content[link.start() + len("<a") : link.end() - len("</a>")]
            + " {% bs_icon 'box-arrow-up-right' extra_classes='external-link-icon' %}"
            + content[link.end() - len("</a>") :]
        )
    template = Template("{% load bootstrap_icons %}" + content)
    return template.render(Context())


@register.filter(name="touchify_abbreviations")
def touchify_abbreviations(content):
    abbreviations = re.finditer("<abbr[^>]*>[^<]*", content)
    for link in reversed(list(abbreviations)):
        content = content[: link.start() + 5] + " tabindex=0" + content[link.start() + 5 :]
    template = Template("{% load bootstrap_icons %}" + content)
    return template.render(Context())


@register.filter(name="markdown")
def markdown(value):
    return render_markdown(value)


@register.filter(name="get_link_for_group")
def get_link_for_group(minutes_creation_links, group):
    return minutes_creation_links[group.id]


@register.filter(name="non_empty")
def toc_non_empty(toc):
    toc_links = re.findall(r'<a href="#[^"]*"', toc)
    return toc and len(toc_links) > 0
