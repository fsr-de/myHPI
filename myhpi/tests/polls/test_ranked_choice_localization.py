from datetime import datetime, timedelta

from wagtail.models import Locale

from myhpi.polls.models import PollList, RankedChoiceOption, RankedChoicePoll
from myhpi.tests.core.utils import MyHPIPageTestCase, ensure_ancestors_translated


def create_ranked_choice_poll_with_translation(base_poll, locale_code="de"):
    de_locale, _ = Locale.objects.get_or_create(language_code=locale_code)
    ensure_ancestors_translated(base_poll, de_locale)
    translated_poll = base_poll.copy_for_translation(de_locale)
    translated_poll.title = base_poll.title + " (DE)"
    translated_poll.save()
    for option in base_poll.options.all():
        option.__class__.objects.create(
            name=option.name + " (DE)",
            description=option.description,
            poll=translated_poll,
        )
    return translated_poll


class RankedChoicePollLocalizationTests(MyHPIPageTestCase):
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
        self.poll = RankedChoicePoll(
            title="SLASH 1999",
            slug="slash-1999",
            description="Who should win the SLASH 1999?",
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            eligible_groups=[self.test_data["groups"][0]],
            results_visible=True,
            visible_for=[self.test_data["groups"][0]],
            is_public=True,
        )
        self.poll_list.add_child(instance=self.poll)
        self.option_alice = RankedChoiceOption.objects.create(name="Alice", poll=self.poll)
        self.option_bob = RankedChoiceOption.objects.create(name="Bob", poll=self.poll)
        self.translated_poll = create_ranked_choice_poll_with_translation(self.poll)

    def test_vote_affects_canonical_poll(self):
        self.sign_in_as_student()
        # Vote via translated poll, but use canonical poll's option IDs
        canonical_option = self.option_alice
        # Provide both options to ensure form is valid
        form_data = {f"option_{self.option_alice.pk}": 1, f"option_{self.option_bob.pk}": 2}
        self.client.post(self.translated_poll.url, data=form_data, follow=True)
        self.assertEqual(self.poll.already_voted.count(), 1)
        self.assertFalse(self.translated_poll.already_voted.exists())

    def test_cannot_vote_twice_in_different_locales(self):
        self.sign_in_as_student()
        # Vote in canonical poll
        form_data = {f"option_{self.option_alice.pk}": 1, f"option_{self.option_bob.pk}": 2}
        self.client.post(self.poll.url, data=form_data, follow=True)
        # Try to vote in translated poll, use canonical poll's option IDs
        form_data = {f"option_{self.option_alice.pk}": 1, f"option_{self.option_bob.pk}": 2}
        response = self.client.post(self.translated_poll.url, data=form_data, follow=True)
        self.assertContains(response, "Du darfst nicht abstimmen", status_code=200)
        self.assertEqual(self.poll.already_voted.count(), 1)

    def test_results_aggregated_in_canonical_poll(self):
        self.sign_in_as_student()
        form_data = {f"option_{self.option_alice.pk}": 1, f"option_{self.option_bob.pk}": 2}
        self.client.post(self.poll.url, data=form_data, follow=True)
        # Results in translated poll should reflect canonical poll
        self.assertEqual(self.poll.ballots.count(), 1)
        self.assertEqual(self.translated_poll.ballots.count(), 0)
