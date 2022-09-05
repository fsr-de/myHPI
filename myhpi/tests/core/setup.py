from django.contrib.auth.models import Group, User
from wagtail.models import Site

from myhpi.core.models import (
    FirstLevelMenuItem,
    InformationPage,
    Minutes,
    MinutesList,
    RootPage,
    SecondLevelMenuItem,
)


def create_users():
    return [
        User.objects.create(
            first_name="Admin",
            last_name="Nimda",
            username="admin",
            is_superuser=True,
            email="admin@example.com",
            password="123456",
        ),
        User.objects.create(
            first_name="Max",
            last_name="Mustermann",
            username="max.mustermann",
            email="max@example.com",
            password="123456",
        ),
        User.objects.create(
            first_name="Monika",
            last_name="Musterfrau",
            username="monika.musterfrau",
            email="monika@example.com",
            password="123456",
        ),
    ]


def create_groups(users):
    superuser, student, student_representative = users
    students = Group.objects.create(name="Students")
    fsr = Group.objects.create(name="Student Representative Group")

    students.user_set.add(superuser)
    students.user_set.add(student)
    students.user_set.add(student_representative)
    fsr.user_set.add(superuser)
    fsr.user_set.add(student_representative)

    return students, fsr


def create_basic_page_structure():
    root_page = RootPage.objects.create(
        title="myHPI",
        slug="myhpi",
        body="This is the root page.",
        author_visible=False,
        is_public=True,
        path="00010002",
        depth=2,
    )
    # Remove dummy site
    Site.objects.all()[0].delete()
    Site.objects.create(
        hostname="localhost", port=80, site_name="myHPI", root_page=root_page, is_default_site=True
    )
    information_menu = FirstLevelMenuItem(
        title="Information",
        show_in_menus=True,
        path="000100020001",
        depth=3,
        is_public=True,
        slug="information",
    )
    student_representation_menu = FirstLevelMenuItem(
        title="Student representation",
        is_public=False,
        show_in_menus=True,
        slug="student-representation",
    )
    root_page.add_child(instance=information_menu)
    root_page.add_child(instance=student_representation_menu)
    fsr_menu = SecondLevelMenuItem(
        title="Student representative group", show_in_menus=True, is_public=False, slug="fsr"
    )
    student_representation_menu.add_child(instance=fsr_menu)

    return {
        "root_page": root_page,
        "information_menu": information_menu,
        "student_representation_menu": student_representation_menu,
        "fsr_menu": fsr_menu,
    }


def create_information_pages(groups, parent):
    students, fsr = groups

    common_page = InformationPage(
        title="Common Page",
        body="A common page for all students.",
        slug="common-page",
        visible_for=[students, fsr],
        depth=4,
        path="0001000200010001",
        is_public=False,
        author_visible=True,
    )
    private_page = InformationPage(
        title="Private Page",
        body="A page only for the student representative group.",
        slug="private-page",
        visible_for=[fsr],
        depth=4,
        path="0001000200010002",
        is_public=False,
        author_visible=True,
    )
    public_page = InformationPage(
        title="Public Page",
        body="A page for everyone.",
        slug="public-page",
        is_public=True,
        depth=4,
        path="0001000200010003",
        author_visible=False,
    )
    parent.add_child(instance=common_page)
    parent.add_child(instance=private_page)
    parent.add_child(instance=public_page)

    return [common_page, private_page, public_page]


def setup_minutes(group, students_group, parent, user):
    minutes_list = MinutesList(
        title="Student representative group minutes",
        group=group,
        is_public=False,
        slug="minutes",
        visible_for=[students_group, group],
    )
    minutes = [
        Minutes(
            title="First minutes",
            date="2022-01-01",
            is_public=False,
            visible_for=[students_group, group],
            moderator=user,
            author=user,
            participants=[user],
            text="These are the first minutes.",
            slug="first-minutes",
        ),
        Minutes(
            title="Second minutes",
            date="2022-02-02",
            is_public=False,
            visible_for=[students_group, group],
            moderator=user,
            author=user,
            participants=[user],
            text="These are the second minutes.",
            slug="second-minutes",
        ),
        Minutes(
            title="Private minutes",
            date="2022-03-03",
            is_public=False,
            visible_for=[group],
            moderator=user,
            author=user,
            participants=[user],
            text="These minutes are private.",
            slug="private-minutes",
        ),
        Minutes(
            title="Unpublished minutes",
            date="2022-04-04",
            is_public=False,
            live=False,
            visible_for=[group],
            moderator=user,
            author=user,
            participants=[user],
            text="These minutes are unpublished.",
            slug="unpublished-minutes",
        ),
        Minutes(
            title="Recent minutes",
            date="2022-05-05",
            is_public=False,
            visible_for=[students_group, group],
            moderator=user,
            author=user,
            participants=[user],
            text="These minutes are the most recent.",
            slug="recent-minutes",
        ),
    ]
    parent.add_child(instance=minutes_list)
    for m in minutes:
        minutes_list.add_child(instance=m)
    return minutes, minutes_list


def setup_data():
    users = create_users()
    groups = create_groups(users)
    basic_pages = create_basic_page_structure()
    information_pages = create_information_pages(groups, basic_pages["information_menu"])
    minutes, minutes_list = setup_minutes(groups[1], groups[0], basic_pages["fsr_menu"], users[2])

    return {
        "users": users,
        "groups": groups,
        "pages": information_pages,
        "minutes": minutes,
        "minutes_list": minutes_list,
    }
