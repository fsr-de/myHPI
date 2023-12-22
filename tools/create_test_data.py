import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myhpi.settings")
django.setup()
import random

from django.contrib.auth.models import Group, Permission, User
from django.core.files import File
from django.db import IntegrityError
from wagtail.contrib.redirects.models import Redirect
from wagtail.documents.models import Document
from wagtail.models import Collection, GroupCollectionPermission

from myhpi.core.models import (
    AbbreviationExplanation,
    BasePage,
    FirstLevelMenuItem,
    InformationPage,
    Minutes,
    MinutesLabel,
    MinutesList,
    RootPage,
    SecondLevelMenuItem,
)


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

    groups = []

    root_collection = Collection.get_first_root_node()

    for group_name in test_groups:
        group = Group.objects.create(name=group_name)
        groups.append(group)

        group_collection = root_collection.add_child(name=f"{group_name} collection")
        group_collection.save()
        GroupCollectionPermission.objects.create(
            group=group,
            collection=group_collection,
            permission=Permission.objects.get(
                content_type__app_label="wagtaildocs", codename="add_document"
            ),
        )
        GroupCollectionPermission.objects.create(
            group=group,
            collection=group_collection,
            permission=Permission.objects.get(
                content_type__app_label="wagtaildocs", codename="change_document"
            ),
        )
        GroupCollectionPermission.objects.create(
            group=group,
            collection=group_collection,
            permission=Permission.objects.get(
                content_type__app_label="wagtaildocs", codename="choose_document"
            ),
        )

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


def create_some_pages(users, groups):
    root_page = RootPage.objects.get()

    # Create information pages
    information_page_root = root_page.add_child(
        instance=FirstLevelMenuItem(
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
    student_rep_group = root_page.add_child(
        instance=FirstLevelMenuItem(
            title="Student Representatives",
            slug="fsr",
            show_in_menus=True,
            is_public=True,
        )
    )
    student_rep_overview = student_rep_group.add_child(
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
    student_rep_minutes = student_rep_group.add_child(
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
            guests="",
            body=generate_text(),
        )
        student_rep_minutes.add_child(instance=minutes)
        labels = random.sample(minutes_labels, random.randint(0, 2))
        for label in labels:
            minutes.labels.add(label)
        minutes.save()


def main():
    # Superuser is created manually via createsuperuser command
    users, groups = create_users_and_groups()
    pages = create_some_pages(users, groups)


if __name__ == "__main__":
    main()
