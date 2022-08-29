import django
from django.test import TestCase

django.setup()

from myhpi.core.markdown.extensions import EnterLeavePreprocessor


# class TestMinuteExtensions(TestCase):
#     def test_enter(self):
#         elp = EnterLeavePreprocessor()
#         text = [
#             "|enter|(12:00)(First Last)",
#             "|enter|(12:00)(Prof. First Last)",
#             "|enter|(12:00)(Prof. First Last)(Means)",
#             "|leave|(12:00)(Prof. First Last)",
#             "|enter|(12:00)(Prof. First Last (Special Role))",
#         ]
#         result = elp.run(text)
#         self.assertEqual(
#             result,
#             [
#                 "*12:00: First Last enters the meeting*  ",
#                 "*12:00: Prof. First Last enters the meeting*  ",
#                 "*12:00: Prof. First Last enters the meeting via Means*  ",
#                 "*12:00: Prof. First Last leaves the meeting*  ",
#                 "*12:00: Prof. First Last (Special Role) enters the meeting*  ",
#             ],
#         )
