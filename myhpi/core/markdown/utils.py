import markdown
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from wagtail.models import Locale
from wagtailmarkdown.utils import _get_markdown_kwargs, _sanitise_markdown_html

from myhpi.core.markdown.extensions import MinuteExtension


def render_markdown(text, context=None, with_abbreveations=True):
    """
    Turn markdown into HTML.
    """
    if context is None or not isinstance(context, dict):
        context = {}
    markdown_html, toc = _transform_markdown_into_html(text, with_abbreviations=with_abbreveations)
    sanitised_markdown_html = _sanitise_markdown_html(markdown_html)
    return mark_safe(sanitised_markdown_html), mark_safe(toc)


def _transform_markdown_into_html(text, with_abbreviations):
    from myhpi.core.models import AbbreviationExplanation

    markdown_kwargs = _get_markdown_kwargs()
    markdown_kwargs["extensions"].append(
        MinuteExtension()
    )  # should be in settings.py, but module lookup doesn't work
    md = markdown.Markdown(**markdown_kwargs)
    abbreviations = "\n\n" + (
        "\n".join(
            [
                f"*[{abbr.abbreviation}]: {abbr.explanation}"
                for abbr in AbbreviationExplanation.objects.filter(locale=Locale.get_active())
            ]
        )
    )
    text = smart_str(text) + abbreviations if with_abbreviations else smart_str(text)
    return md.convert(text), md.toc
