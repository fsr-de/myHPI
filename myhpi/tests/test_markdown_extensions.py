import re

from django.test import TestCase
from django.utils.translation import activate


from myhpi.core.markdown.extensions import (
    BreakPreprocessor,
    EnterLeavePreprocessor,
    HeadingLevelPreprocessor,
    InternalLinkPattern,
    QuorumPreprocessor,
    ResolutionPreprocessor,
    StartEndPreprocessor,
    VotePreprocessor,
)


class TestMarkdownExtensions(TestCase):
    def test_vote_preprocessor(self):
        vp = VotePreprocessor()
        text = ["[2|3|4]", "[a|b|c]"]  # Second line is not processed
        result = vp.run(text)
        self.assertEqual(result, ["**[2|3|4]**", "[a|b|c]"])

    def test_start_end_preprocessor(self):
        activate("en")
        sep = StartEndPreprocessor()
        text = ["|start|(12:00)", "|end|(16:00)"]
        result = sep.run(text)
        self.assertEqual(result, ["*Begin of meeting: 12:00*  ", "*End of meeting: 16:00*  "])

    def test_break_preprocessor(self):
        activate("en")
        bp = BreakPreprocessor()
        text = ["|break|(12:00)(13:00)"]
        result = bp.run(text)
        self.assertEqual(result, ["*Meeting break: 12:00 – 13:00*"])

    def test_quorum_preprocessor(self):
        activate("en")
        qp = QuorumPreprocessor()
        text = ["|quorum|(3/8)", "|quorum|(4/8)"]
        result = qp.run(text)
        self.assertEqual(result, ["*3/8 present → not quorate*  ", "*4/8 present → quorate*  "])

    def test_resolution_preprocessor(self):
        activate("en")
        qp = ResolutionPreprocessor()
        text = [
            "|resolution|(1000000)(Bouncy Castle)(Fun)",
            "|resolution|(0.42)(Paper clips)(Office)",
        ]
        result = qp.run(text)
        self.assertEqual(
            result,
            [
                "* We decide to spend up to 1000000 € for Bouncy Castle (Budget: Fun).",
                "* We decide to spend up to 0.42 € for Paper clips (Budget: Office).",
            ],
        )

    def test_enter_leave_preprocessor(self):
        activate("en")
        elp = EnterLeavePreprocessor()
        text = [
            "|enter|(12:00)(First Last)",
            "|enter|(12:00)(Prof. First Last)",
            "|enter|(12:00)(Prof. First Last)(Means)",
            "|leave|(12:00)(Prof. First Last)",
        ]
        result = elp.run(text)
        self.assertEqual(
            result,
            [
                "*12:00: First Last enters the meeting*  ",
                "*12:00: Prof. First Last enters the meeting*  ",
                "*12:00: Prof. First Last enters the meeting via Means*  ",
                "*12:00: Prof. First Last leaves the meeting*  ",
            ],
        )

    def test_heading_level_preprocessor(self):
        hlp = HeadingLevelPreprocessor()
        text = [
            "# Heading 1",
            "## Heading 2",
            "### Heading 3",
            "#### Heading 4",
            "##### Heading 5",
            "###### Heading 6",
        ]
        result = hlp.run(text)
        self.assertEqual(
            result,
            [
                "## Heading 1",
                "### Heading 2",
                "#### Heading 3",
                "##### Heading 4",
                "###### Heading 5",
                "###### Heading 6",
            ],
        )

    def test_internal_link_preprocessor(self):
        ilp = InternalLinkPattern(InternalLinkPattern.default_pattern())

        from myhpi.tests.core.setup import setup_data

        test_data = setup_data()
        test_page = test_data["pages"][0]
        text = f"[Page title](page:{test_page.id})"
        el, _, _ = ilp.handleMatch(re.match(ilp.pattern, text))
        self.assertEqual(el.attrib["href"], test_page.localized.get_url())
