import re

import markdown
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from markdown import Extension
from markdown.inlinepatterns import LinkInlineProcessor
from markdown.preprocessors import Preprocessor
from wagtail.core.models import Page


class MinutesBasePreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []

        for line in lines:
            if line.strip():
                for pattern, method in self.patterns:
                    line = re.sub(pattern, method, line, flags=re.UNICODE)
            new_lines.append(line)

        return new_lines


class VotePreprocessor(MinutesBasePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns = [
            (r"\[(\d+)\|(\d+)\|(\d+)\]", self.votify),
        ]

    def votify(self, match):
        num_positive_votes = match.group(1)
        num_negative_votes = match.group(2)
        num_abstentions = match.group(3)

        return "**[{}|{}|{}]**".format(num_positive_votes, num_negative_votes, num_abstentions)


class StartEndPreprocessor(MinutesBasePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns = [
            (r"\|start\|\((\d+):(\d+)\)", self.startify),
            (r"\|end\|\((\d+):(\d+)\)", self.endify),
        ]

    def startify_or_endify(self, match, event):
        hour = match.group(1)
        minute = match.group(2)
        return "*{event}: {hour}:{minute}*  ".format(event=event, hour=hour, minute=minute)

    def startify(self, match):
        return self.startify_or_endify(match, _("Begin of meeting"))

    def endify(self, match):
        return self.startify_or_endify(match, _("End of meeting"))


class BreakPreprocessor(MinutesBasePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns = [
            (r"\|break\|\(([0-9:]+)\)\(([0-9:]+)\)", self.breakify),
        ]

    def breakify(self, match):
        time_start_break = match.group(1)
        time_end_break = match.group(2)

        return _("*Meeting break: {time_start_break} – {time_end_break}*").format(
            time_start_break=time_start_break,
            time_end_break=time_end_break,
        )


class QuorumPrepocessor(MinutesBasePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns = [
            (r"\|quorum\|\((\d+)/(\d+)\)", self.quorumify),
        ]

    def quorumify(self, match):
        num_participants = int(match.group(1))
        max_num_participants = int(match.group(2))
        quorate = (
            _("quorate") if num_participants / max_num_participants >= 0.5 else _("not quorate")
        )

        return _("*{num_participants}/{max_num_participants} present → {quorate}*  ").format(
            num_participants=num_participants,
            max_num_participants=max_num_participants,
            quorate=quorate,
        )


class EnterLeavePreprocessor(MinutesBasePreprocessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns = [
            (
                r"\|enter\|\(([0-9:]+)\)\(([^\)\(]+)\)(\((?P<mean_of_participation>.*?)\))?",
                self.enterify,
            ),
            (
                r"\|leave\|\(([0-9:]+)\)\(([^\)\(]+)\)",
                self.leavify
            ),
        ]

    def enter_or_leavify(self, match, event):
        time = match.group(1)
        name = match.group(2)
        via_description = match.groupdict().get("mean_of_participation", None)

        if via_description is None:
            message = _("*{time}: {name} {event} the meeting*  ").format(
                time=time, name=name, event=event
            )
        else:
            message = _(
                "*{time}: {name} {event} the meeting via {mean_of_participation}*  "
            ).format(
                time=time,
                name=name,
                event=event,
                mean_of_participation=via_description,
            )
        return message

    def enterify(self, match):
        return self.enter_or_leavify(match, _("enters"))

    def leavify(self, match):
        return self.enter_or_leavify(match, _("leaves"))


class InternalLinkPattern(LinkInlineProcessor):
    def handleMatch(self, m, data=None):
        el = markdown.util.etree.Element("a")
        try:
            el.set("href", self.url(m.group("id")))
            el.text = markdown.util.AtomicString(m.group("title"))
        except ObjectDoesNotExist:
            el.text = markdown.util.AtomicString(_("[missing link]"))
        return el, m.start(0), m.end(0)

    def url(self, id):
        return Page.objects.get(id=id).localized.get_url()


class MinuteExtension(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(VotePreprocessor(md), "votify", 200)
        md.preprocessors.register(StartEndPreprocessor(md), "start_or_endify", 200)
        md.preprocessors.register(BreakPreprocessor(md), "breakify", 200)
        md.preprocessors.register(QuorumPrepocessor(md), "quorumify", 200)
        md.preprocessors.register(EnterLeavePreprocessor(md), "enter_or_leavify", 200)
        md.inlinePatterns.register(
            InternalLinkPattern(r"\[(?P<title>[^\[]+)\]\(page:(?P<id>\d+)\)", md),
            "InternalLinkPattern",
            200,
        )


def makeExtension():
    return MinuteExtension()
