import html2text
from wagtail_localize.segments import (
    OverridableSegmentValue,
    StringSegmentValue,
    TemplateSegmentValue,
)
from wagtail_localize.segments.extract import quote_path_component
from wagtail_localize.segments.ingest import organise_template_segments
from wagtail_localize.strings import extract_strings, restore_strings
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.utils import render_markdown


class CustomMarkdownField(MarkdownField):
    def get_translatable_segments(self, value):
        template, strings = extract_strings(render_markdown(value))

        # Find all unique href values
        hrefs = set()
        for string, attrs in strings:
            for tag_attrs in attrs.values():
                if "href" in tag_attrs:
                    hrefs.add(tag_attrs["href"])

        return (
            [TemplateSegmentValue("", "html", template, len(strings))]
            + [StringSegmentValue("", string, attrs=attrs) for string, attrs in strings]
            + [OverridableSegmentValue(quote_path_component(href), href) for href in sorted(hrefs)]
        )

    def restore_translated_segments(self, value, field_segments):
        format, template, strings = organise_template_segments(field_segments)
        return html2text.html2text(restore_strings(template, strings), bodywidth=0)
