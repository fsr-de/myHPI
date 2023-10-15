from dataclasses import dataclass
from myhpi.core.widgets import AttachmentSelectWidget
from myhpi.tests.core.utils import MyHPIPageTestCase

from django.forms.models import ModelChoiceIteratorValue


class WidgetTests(MyHPIPageTestCase):
    def setUp(self):
        super().setUp()

    def test_attachment_select_widget(self):
        self.sign_in_as_student()
        # student has access to document 1, not document 2
        choices = list(
            map(
                lambda doc: (ModelChoiceIteratorValue(doc.id, doc), doc.title),
                self.test_data["documents"],
            )
        )
        widget = AttachmentSelectWidget(user=self.student, choices=choices)
        optgroups = widget.optgroups("attachments", [])
        self.assertEqual(len(optgroups), 1)

        widget = AttachmentSelectWidget(user=self.student_representative, choices=choices)
        optgroups = widget.optgroups("attachments", [])
        self.assertEqual(len(optgroups), 2)
