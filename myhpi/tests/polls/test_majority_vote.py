from datetime import datetime, timedelta

from wagtail.models import Locale

from myhpi.polls.models import MajorityVoteChoice, MajorityVotePoll, PollList
from myhpi.tests.core.utils import MyHPIPageTestCase, ensure_ancestors_translated


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
            eligible_groups=[self.test_data["groups"][0]],
            visible_for=[self.test_data["groups"][0]],
            max_allowed_answers=1,
            results_visible=False,
            is_public=True,
        )

        self.poll_list.add_child(instance=self.poll)

        self.choice_good = MajorityVoteChoice(
            text="Good",
            page=self.poll,
            votes=0,
        )
        self.choice_good.save()
        self.choice_bad = MajorityVoteChoice(
            text="Bad",
            page=self.poll,
            votes=0,
        )
        self.choice_bad.save()

    def test_can_vote_once(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        self.poll.already_voted.add(self.student)
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
        response = self.client.post(self.poll.url, data={"choice": []}, follow=True)
        self.assertContains(response, "You must select at least one choice.")
        self.assertTrue(self.poll.can_vote(self.student))

    def test_post_vote_too_many_choices(self):
        self.sign_in_as_student()
        self.assertTrue(self.poll.can_vote(self.student))
        response = self.client.post(
            self.poll.url, data={"choice": [self.choice_good.id, self.choice_bad.id]}, follow=True
        )
        self.assertContains(response, "You can only select up to 1 options.", 1)
        self.assertTrue(self.poll.can_vote(self.student))

    def test_post_vote_before_start_date(self):
        self.sign_in_as_student()
        self.poll.start_date = datetime.now() + timedelta(days=1)
        self.poll.save()
        self.assertFalse(self.poll.can_vote(self.student))
        response = self.client.post(
            self.poll.url, data={"choice": [self.choice_good.id]}, follow=True
        )
        self.assertContains(response, "You've accessed this page outside of the voting period.")


def create_poll_with_translation(base_poll, locale_code="de"):
    # Create a translation of the poll in another locale
    de_locale, _ = Locale.objects.get_or_create(language_code=locale_code)
    # Ensure ancestors are translated (wagtail requires all ancestor pages to be translated)
    ensure_ancestors_translated(base_poll, de_locale)
    translated_poll = base_poll.copy_for_translation(de_locale)
    translated_poll.title = base_poll.title + " (DE)"
    translated_poll.save()
    # Copy choices
    for choice in base_poll.choices.all():
        MajorityVoteChoice.objects.create(
            text=choice.text + " (DE)",
            page=translated_poll,
            votes=0,
        )
    return translated_poll


class PollLocalizationTests(MyHPIPageTestCase):
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
            eligible_groups=[self.test_data["groups"][0]],
            visible_for=[self.test_data["groups"][0]],
            max_allowed_answers=1,
            results_visible=False,
            is_public=True,
        )
        self.poll_list.add_child(instance=self.poll)
        self.choice_good = MajorityVoteChoice(
            text="Good",
            page=self.poll,
            votes=0,
        )
        self.choice_good.save()
        self.choice_bad = MajorityVoteChoice(
            text="Bad",
            page=self.poll,
            votes=0,
        )
        self.choice_bad.save()
        self.translated_poll = create_poll_with_translation(self.poll)

    def test_vote_affects_canonical_poll(self):
        self.sign_in_as_student()
        # Vote via translated poll, but use canonical poll's choice ID
        canonical_choice = self.choice_good
        self.client.post(
            self.translated_poll.url,
            data={"choice": [canonical_choice.id]},
        )
        # Canonical poll should have the vote
        self.assertEqual(self.poll.already_voted.count(), 1)
        self.assertFalse(self.translated_poll.already_voted.exists())

    def test_cannot_vote_twice_in_different_locales(self):
        self.sign_in_as_student()
        # Vote in canonical poll
        self.client.post(
            self.poll.url,
            data={"choice": [self.choice_good.id]},
        )
        # Try to vote in translated poll, use canonical poll's choice ID
        canonical_choice = self.choice_good
        response = self.client.post(
            self.translated_poll.url,
            data={"choice": [canonical_choice.id]},
        )
        self.assertContains(response, "Du darfst nicht abstimmen", status_code=200)
        self.assertEqual(self.poll.already_voted.count(), 1)
