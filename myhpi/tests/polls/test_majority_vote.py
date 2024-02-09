from datetime import datetime, timedelta

from myhpi.polls.models import MajorityVotePoll, MajorityVoteChoice, PollList
from myhpi.tests.core.utils import MyHPIPageTestCase


class PollTests(MyHPIPageTestCase):
    def setUp(self):
        super().setUp()
        self.poll_list = PollList(
            title="Polls",
            slug="polls",
            path="0001000200010005",
            depth=4,
            is_public=True,
        )
        self.information_menu.add_child(instance=self.poll_list)

        self.poll = MajorityVotePoll(
            title="How are you?",
            slug="how-are-you",
            question="How are you?",
            description="This is a poll to check how you are.",
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            max_allowed_answers=1,
            results_visible=False,
            is_public=True,
        )

        self.poll_list.add_child(instance=self.poll)

        self.choice_good = PollChoice(
            text="Good",
            page=self.poll,
            votes=0,
        )
        self.choice_good.save()
        self.choice_bad = PollChoice(
            text="Bad",
            page=self.poll,
            votes=0,
        )
        self.choice_bad.save()

    def test_can_vote_once(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        self.poll.participants.add(self.student)
        self.assertFalse(self.poll.can_vote(self.student))

    def test_post_vote(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        self.client.post(
            self.poll.url,
            data={"choice": [self.choice_good.id]},
        )
        self.choice_good.refresh_from_db()
        self.assertEqual(self.choice_good.votes, 1)
        self.assertEqual(self.choice_good.percentage(), 100)
        self.assertEqual(self.choice_bad.percentage(), 0)
        self.assertFalse(self.poll.can_vote(self.student))

    def test_post_vote_invalid_choice(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        self.client.post(
            self.poll.url,
            data={"choice": [self.choice_good.id + 9999]},
        )
        self.choice_good.refresh_from_db()
        self.assertEqual(self.choice_good.votes, 0)
        self.assertTrue(self.poll.can_vote(self.student))

    def test_post_vote_no_choice(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        response = self.client.post(
            self.poll.url,
            data={"choice": []},
        )
        self.assertContains(response, "You must select at least one choice.")
        self.assertTrue(self.poll.can_vote(self.student))

    def test_post_vote_too_many_choices(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        response = self.client.post(
            self.poll.url,
            data={"choice": [self.choice_good.id, self.choice_bad.id]},
        )
        self.assertContains(response, "You can only select up to 1 options.", 1)
        self.assertTrue(self.poll.can_vote(self.student))

    def test_post_vote_before_start_date(self):
        self.sign_in_as_student()
        self.poll.start_date = datetime.now() + timedelta(days=1)
        self.poll.save()
        self.assertTrue(self.poll.can_vote(self.student))
        response = self.client.post(
            self.poll.url, data={"choice": [self.choice_good.id]}, follow=True
        )
        self.assertContains(response, "This poll has not yet started.")
        self.assertTrue(self.poll.can_vote(self.student))
