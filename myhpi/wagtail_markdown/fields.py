# vim:sw=4 ts=4 et:
# Copyright (c) 2015 Torchbox Ltd.
# felicity@torchbox.com 2015-09-14
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#

import html2text
from django.db.models import TextField
from wagtail_localize.segments import (
    OverridableSegmentValue,
    StringSegmentValue,
    TemplateSegmentValue,
)
from wagtail_localize.segments.extract import quote_path_component
from wagtail_localize.segments.ingest import organise_template_segments
from wagtail_localize.strings import extract_strings, restore_strings

from .utils import render_markdown
from .widgets import MarkdownTextarea


class MarkdownField(TextField):
    def formfield(self, **kwargs):
        defaults = {"widget": MarkdownTextarea}
        defaults.update(kwargs)
        return super(MarkdownField, self).formfield(**defaults)

    def get_translatable_segments(self, value):
        template, strings = extract_strings(render_markdown(value, with_abbreveations=False)[0])

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
        return html2text.html2text(restore_strings(template, strings))
