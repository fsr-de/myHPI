from datetime import datetime, timedelta

from django.test.utils import tag

from myhpi.polls.models import (
    PollList,
    RankedChoiceBallot,
    RankedChoiceBallotEntry,
    RankedChoiceOption,
    RankedChoicePoll,
)
from myhpi.tests.core.utils import MyHPIPageTestCase


class RankedChoiceAlgorithmTests(MyHPIPageTestCase):
    def setUp(self):
        super().setUp()

        method = getattr(self, self._testMethodName)
        tags = getattr(method, "tags", {})
        if "skip_setup" in tags:
            return
        self.setup_poll()

        self.options = {
            "alice": RankedChoiceOption.objects.create(name="Alice", poll=self.poll),
            "bob": RankedChoiceOption.objects.create(name="Bob", poll=self.poll),
            "charlie": RankedChoiceOption.objects.create(name="Charlie", poll=self.poll),
            "dora": RankedChoiceOption.objects.create(name="Dora", poll=self.poll),
        }

    def setup_poll(self):
        self.poll_list = PollList(
            title="Polls",
            slug="polls",
            path="0001000200010005",
            depth=4,
            is_public=True,
        )
        self.information_menu.add_child(instance=self.poll_list)

        self.poll = RankedChoicePoll(
            title="SLASH 1999",
            slug="slash-1999",
            description="Who should win the SLASH 1999?",
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            results_visible=False,
            is_public=True,
        )

        self.poll_list.add_child(instance=self.poll)

    def cast_ballots(self, template_ballots):
        for template_ballot in template_ballots:
            ballot = RankedChoiceBallot.objects.create(poll=self.poll)
            ballot.save()

            for idx, template_entry in enumerate(template_ballot):
                RankedChoiceBallotEntry.objects.create(
                    ballot=ballot, option=self.options[template_entry], rank=idx
                )

    def test_can_two_first_places(self):
        self.cast_ballots([["alice", "bob"], ["bob", "alice"]])
        self.assertEqual(
            self.poll.calculate_ranking(),
            [(1, "Alice", 1), (1, "Bob", 1), (3, "Charlie", 0), (3, "Dora", 0)],
        )

    def test_three_first_places(self):
        self.cast_ballots([["alice", "bob"], ["bob", "alice"], ["charlie"]])
        self.assertEqual(
            self.poll.calculate_ranking(),
            [(1, "Alice", 1), (1, "Bob", 1), (1, "Charlie", 1), (4, "Dora", 0)],
        )

    def test_runoff_with_skips(self):
        self.cast_ballots(
            ([["alice", "charlie", "bob"]] * 10)
            + ([["bob", "alice", "charlie"]] * 12)
            + ([["charlie", "dora", "alice", "bob"]] * 9)
            + ([["dora", "alice", "charlie"]] * 1)
        )
        self.assertEqual(
            self.poll.calculate_ranking(),
            [(1, "Alice", 32), (2, "Bob", 12), (3, "Charlie", 9), (4, "Dora", 1)],
        )

    def test_no_ballots(self):
        self.assertEqual(
            self.poll.calculate_ranking(),
            [(1, "Alice", 0), (1, "Bob", 0), (1, "Charlie", 0), (1, "Dora", 0)],
        )

    def test_fast(self):
        self.cast_ballots(([["alice", "bob"]] * 1000) + ([["bob", "alice", "charlie"]] * 900))

        start = datetime.datetime.now()
        result = self.poll.calculate_ranking(),
        end = datetime.datetime.now()
        self.assertLessEqual(end - start, timedelta(milliseconds=100))
        self.assertEqual(
            result,
            [(1, "Alice", 1900), (2, "Bob", 900), (3, "Charlie", 0), (3, "Dora", 0)],
        )

    @tag("skip_setup")
    def test_no_options(self):
        self.setup_poll()
        self.assertEqual(self.poll.calculate_ranking(), [])
