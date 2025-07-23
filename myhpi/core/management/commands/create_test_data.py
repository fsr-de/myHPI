import random
from datetime import date

from django.contrib.auth.models import Group, User
from django.core.management import BaseCommand

from myhpi.core.models import (
    AbbreviationExplanation,
    InformationPage,
    MenuItem,
    Minutes,
    MinutesLabel,
    MinutesList,
    RootPage,
)
from myhpi.polls.models import PollList, RankedChoiceOption, RankedChoicePoll
from myhpi.tests.core.setup import create_collections, create_documents


def generate_random_text(words, paragraphs=5, sentences_per_paragraph=5, words_per_sentence=10):
    text = ""
    for _ in range(paragraphs):
        paragraph = ""
        for _ in range(sentences_per_paragraph):
            sentence = " ".join(random.sample(words, words_per_sentence))
            paragraph += sentence.capitalize() + ". "
        text += paragraph + "\n\n"
    return text.strip()


def generate_text():
    text = ""
    for _ in range(random.randint(1, 5)):
        text += f"# {random.choice(sample_words).capitalize()} {random.choice(sample_words).capitalize()}\n\n"
        text += (
            generate_random_text(
                sample_words,
                paragraphs=random.randint(1, 5),
                sentences_per_paragraph=random.randint(1, 5),
                words_per_sentence=random.randint(5, 15),
            )
            + "\n\n"
        )
    return text.strip()


# List of sample words
sample_words = [
    "lorem",
    "ipsum",
    "dolor",
    "sit",
    "amet",
    "consectetur",
    "adipiscing",
    "elit",
    "sed",
    "do",
    "eiusmod",
    "tempor",
    "incididunt",
    "ut",
    "labore",
    "et",
    "dolore",
    "magna",
    "aliqua",
    "HPI",
    "FSR",
]


def create_users_and_groups():
    test_groups = [
        "Student",
        "Student Representative Group",
        "Study Council",
        "Student Representatives",
        "Frisbee Club",
    ]
    user_data = [
        ("Max", "Mustermensch", [0, 1, 2, 3, 4]),
        ("Monika", "Mustermensch", [0, 1, 3]),
        ("Peter", "Silie", [0, 1, 3]),
        ("Iris", "Blau", [0, 1, 3, 4]),
        ("Otto", "Normalverbraucher", [0, 2, 3]),
        ("Ronja", "Räubertochter", [0, 2, 3, 4]),
        ("Hans", "Dampf", [0, 4]),
        ("Karl", "Koch", [0]),
        ("Klaus", "Kleber", [0]),
        ("Berta", "Beispiel", [0]),
        ("Hans", "Wurst", [0]),
        ("Anna", "Lyse", [0]),
    ]

    groups = [Group.objects.create(name=group_name) for group_name in test_groups]

    users = []
    for user_spec in user_data:
        user = User.objects.create_user(
            username=f"{user_spec[0]}.{user_spec[1]}",
            email=f"{user_spec[0]}.{user_spec[1]}@student.hpi.de",
            password="test",
            first_name=user_spec[0],
            last_name=user_spec[1],
        )
        for group_id in user_spec[2]:
            user.groups.add(groups[group_id])
        users.append(user)

    return users, groups


def create_abbreviation_explanations():
    AbbreviationExplanation.objects.create(
        abbreviation="hpi",
        explanation="Hasso Plattner Institute",
    )
    AbbreviationExplanation.objects.create(
        abbreviation="fsr",
        explanation="Student Representative Group",
    )


def create_some_pages(users, groups, documents):
    root_page = RootPage.objects.get()

    # Create information pages
    information_page_root = root_page.add_child(
        instance=MenuItem(
            title="Information",
            slug="information",
            show_in_menus=True,
            is_public=True,
        )
    )
    first_semester_page = information_page_root.add_child(
        instance=InformationPage(
            title="Information for first semester students",
            slug="first-semester",
            show_in_menus=True,
            is_public=True,
            body=generate_text(),
            author_visible=True,
            visible_for=[],
        )
    )
    internal_infos_page = information_page_root.add_child(
        instance=InformationPage(
            title="Internal information",
            slug="internal",
            show_in_menus=True,
            is_public=False,
            body=generate_text(),
            author_visible=True,
            visible_for=[groups[0]],
        )
    )

    # Create student rep pages

    student_rep_menu = root_page.add_child(
        instance=MenuItem(
            title="Student Representatives",
            slug="fsr",
            show_in_menus=True,
            is_public=True,
        )
    )
    student_rep_overview = student_rep_menu.add_child(
        instance=InformationPage(
            title="Student Representatives",
            slug="overview",
            show_in_menus=True,
            is_public=True,
            body=generate_text(),
            author_visible=True,
            visible_for=[],
        )
    )
    student_rep_overview.attachments.add(documents[0])
    student_rep_overview.save()

    # FSR minutes

    student_rep_minutes = student_rep_menu.add_child(
        instance=MinutesList(
            title="Minutes",
            slug="minutes",
            show_in_menus=True,
            is_public=False,
            group=groups[2],
            visible_for=[groups[0]],
        )
    )

    minutes_labels = [MinutesLabel.objects.create(name=sample_words[i]) for i in range(2)]

    for i in range(2, 20):
        minutes = Minutes(
            title="Student representative group meeting",
            date=f"2023-01-{i:02}",
            is_public=False,
            visible_for=[groups[0]],
            moderator=random.choice([users[0], users[1], users[2], users[3]]),
            author=random.choice([users[0], users[1], users[2], users[3]]),
            participants=random.sample(
                [users[0], users[1], users[2], users[3]], random.randint(3, 4)
            ),
            location="FSR-Office" if i % 2 == 0 else "Online",
            guests="",
            body=generate_text(),
        )
        student_rep_minutes.add_child(instance=minutes)
        labels = random.sample(minutes_labels, random.randint(0, 2))
        for label in labels:
            minutes.labels.add(label)
        minutes.save()

    # Study council pages

    study_council_menu = root_page.add_child(
        instance=MenuItem(
            title="Study Council",
            slug="study-council",
            show_in_menus=True,
            is_public=False,
            visible_for=[groups[0]],
        )
    )

    study_council_overview = study_council_menu.add_child(
        instance=InformationPage(
            title="Study Council",
            slug="overview",
            show_in_menus=True,
            is_public=False,
            body=generate_text(),
            author_visible=True,
            visible_for=[groups[0]],
        )
    )

    study_council_minutes_list = study_council_menu.add_child(
        instance=MinutesList(
            title="Minutes",
            slug="minutes",
            show_in_menus=True,
            is_public=False,
            group=groups[2],
            visible_for=[groups[2]],
        )
    )

    study_council_minutes = Minutes(
        title="Study council meeting",
        date="2023-01-01",
        is_public=False,
        visible_for=[groups[2]],
        moderator=users[4],
        author=users[5],
        participants=[users[0], users[4], users[5]],
        guests='["Prof. Essor"]',
        body=generate_text(),
    )
    study_council_minutes_list.add_child(instance=study_council_minutes)
    study_council_minutes.attachments.add(documents[1])
    study_council_minutes.save()

    # Club pages

    club_menu = root_page.add_child(
        instance=MenuItem(
            title="Student Clubs",
            slug="clubs",
            show_in_menus=True,
            is_public=False,
            visible_for=[groups[0]],
        )
    )

    frisbee_club_menu = club_menu.add_child(
        instance=MenuItem(
            title="Frisbee Club",
            slug="frisbee",
            show_in_menus=True,
            is_public=False,
            visible_for=[groups[4]],
        )
    )

    frisbee_club_overview = frisbee_club_menu.add_child(
        instance=InformationPage(
            title="Frisbee Club",
            slug="overview",
            show_in_menus=True,
            is_public=False,
            body=generate_text(),
            author_visible=True,
            visible_for=[groups[4]],
        )
    )

    # Polls

    polls_page = root_page.add_child(
        instance=PollList(
            title="Polls",
            slug="polls",
            show_in_menus=True,
            is_public=True,
            visible_for=[groups[0]],
        )
    )
    slash_1999_poll = polls_page.add_child(
        instance=RankedChoicePoll(
            title="SLASH 1999",
            slug="slash-1999",
            show_in_menus=True,
            is_public=True,
            description=generate_text(),
            start_date=date(1999, 1, 1),
            end_date=date(2999, 12, 31),
            results_visible=False,
            eligible_groups=[groups[0]],
            visible_for=[groups[0]],
        )
    )
    option_alice = RankedChoiceOption(
        name="Alice", description=generate_text(), poll=slash_1999_poll
    )
    option_bob = RankedChoiceOption(name="Bob", description=generate_text(), poll=slash_1999_poll)
    option_charlie = RankedChoiceOption(
        name="Charlie", description=generate_text(), poll=slash_1999_poll
    )
    option_alice.save()
    option_bob.save()
    option_charlie.save()
    slash_1999_poll.options.add(option_alice)
    slash_1999_poll.options.add(option_bob)
    slash_1999_poll.options.add(option_charlie)


class Command(BaseCommand):
    help = "Creates test data (user, pages, etc.) for myHPI."

    def handle(self, *args, **options):
        # Superuser is created manually via createsuperuser command
        users, groups = create_users_and_groups()
        collections = list(create_collections(groups))
        documents = create_documents([collections[1], collections[2]])
        create_abbreviation_explanations()
        create_some_pages(users, groups, documents)
        self.stdout.write(
            self.style.SUCCESS(
                'Test data created succesfully. Remember that you need to create a superuser manually with "python manage.py createsuperuser".'
            )
        )
