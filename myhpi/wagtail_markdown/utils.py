# vim:sw=4 ts=4 et:
# Copyright (c) 2015 Torchbox Ltd.
# felicity@torchbox.com 2015-09-14
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#

import bleach
import markdown
from django.conf import settings
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from markdown.extensions.toc import TocExtension

from .mdx import linker, tables
from .minutes_extensions import MinuteExtension


def render_markdown(text, context=None, with_abbreveations=True):
    """
    Turn markdown into HTML.
    """
    if context is None or not isinstance(context, dict):
        context = {}
    markdown_html, toc = _transform_markdown_into_html(text, with_abbreveations=with_abbreveations)
    sanitised_markdown_html = _sanitise_markdown_html(markdown_html)
    return mark_safe(sanitised_markdown_html), mark_safe(toc)


def _transform_markdown_into_html(text, with_abbreveations):
    from myhpi.core.models import AbbreviationExplanation

    md = markdown.Markdown(**_get_markdown_kwargs())
    abbreveations = "\n" + (
        "\n".join(
            [
                f"*[{abbr.abbreviation}]: {abbr.explanation}"
                for abbr in AbbreviationExplanation.objects.all()
            ]
        )
    )
    text = smart_str(text) + abbreveations if with_abbreveations else smart_str(text)
    return md.convert(text), md.toc


def _sanitise_markdown_html(markdown_html):
    tags = [
        "abbr",
        "p",
        "div",
        "span",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "tt",
        "pre",
        "em",
        "strong",
        "ul",
        "sup",
        "li",
        "dl",
        "dd",
        "dt",
        "code",
        "img",
        "a",
        "table",
        "tr",
        "th",
        "td",
        "tbody",
        "caption",
        "colgroup",
        "thead",
        "tfoot",
        "blockquote",
        "ol",
        "hr",
        "br",
    ]
    attrs = {
        "*": [
            "class",
            "style",
            "id",
        ],
        "abbr": ["title"],
        "a": [
            "href",
            "target",
            "rel",
        ],
        "img": [
            "src",
            "alt",
        ],
        "tr": [
            "rowspan",
            "colspan",
        ],
        "td": [
            "rowspan",
            "colspan",
            "align",
        ],
    }
    allowed_props = [
        "color",
        "background-color",
        "font-family",
        "font-weight",
        "font-size",
        "width",
        "height",
        "text-align",
        "border",
        "border-top",
        "border-bottom",
        "border-left",
        "border-right",
        "padding",
        "padding-top",
        "padding-bottom",
        "padding-left",
        "padding-right",
        "margin",
        "margin-top",
        "margin-bottom",
        "margin-left",
        "margin-right",
    ]
    css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_props)
    return bleach.clean(markdown_html, tags=tags, attributes=attrs)


def _get_markdown_kwargs():
    markdown_kwargs = {}
    markdown_kwargs["extensions"] = [
        "extra",
        "codehilite",
        tables.TableExtension(),
        linker.LinkerExtension(
            {
                "__default__": "wagtail_markdown.mdx.linkers.page",
                "page:": "wagtail_markdown.mdx.linkers.page",
                "image:": "wagtail_markdown.mdx.linkers.image",
                "doc:": "wagtail_markdown.mdx.linkers.document",
            }
        ),
        MinuteExtension(),
        TocExtension(),
        "markdown.extensions.abbr",
    ]

    if hasattr(settings, "WAGTAILMARKDOWN_EXTENSIONS"):
        markdown_kwargs["extensions"] += settings.WAGTAILMARKDOWN_EXTENSIONS

    markdown_kwargs["extension_configs"] = {
        "codehilite": [
            ("guess_lang", False),
        ]
    }
    markdown_kwargs["output_format"] = "html5"
    return markdown_kwargs
