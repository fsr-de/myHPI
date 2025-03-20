import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from myhpi.core.markdown.utils import render_markdown

register = template.Library()


@register.filter(name="highlight_query_markdown")
# select 3 lines around first match and highlight query match
def highlight_query(content, search_query, surrounding_lines=1):
    # if query coincides with page id the search breaks without the extra space
    if search_query.isnumeric():
        search_query = str(search_query) + " "
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if search_query.lower() in line.lower():
            lines[i] = line
            # try finding the last leading heading to include it in the snippet
            trailing_heading = None
            # skip if the current line already is a heading
            if not line.startswith("#"):
                for j in range(i - 1, -1, -1):
                    if lines[j].startswith("#"):
                        trailing_heading = lines[j]
                        break
            # take 3 lines around match
            start = max(0, i - 1)
            end = min(len(lines), i + 2)
            lines = lines[start:end]
            if trailing_heading:
                lines.insert(0, trailing_heading)
            break
    excerpt_max_length = surrounding_lines * 2 + 1
    if len(lines) > excerpt_max_length:
        lines = lines[:excerpt_max_length]
    markdown = "\n".join(lines)
    # Replace search query with bold version but preserve case from markdown
    markdown = re.sub(
        re.compile(f"({search_query})", re.IGNORECASE),
        r"**\1**",
        markdown,
    )
    rendered_markdown = render_markdown(markdown, None, False)[0]
    return rendered_markdown


@register.filter(name="highlight_title")
def highlight_title(title, search_query):
    title = escape(title)
    return mark_safe(
        re.sub(
            re.compile(f"({search_query})", re.IGNORECASE),
            r"<strong>\1</strong>",
            title,
        )
    )
