from django.contrib.auth.models import Group, User
from wagtail.models import Site

from myhpi import settings
from myhpi.core.models import FirstLevelMenuItem, InformationPage, RootPage


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
    FirstLevelMenuItem.objects.create(
        title="Information", show_in_menus=True, path="000100020001", depth=3, is_public=True
    )


def create_information_pages(groups):
    students, fsr = groups

    return [
        InformationPage.objects.create(
            title="Common Page",
            body="A common page for all students.",
            visible_for=[students, fsr],
            depth=4,
            path="0001000200010001",
            is_public=False,
            author_visible=True,
        ),
        InformationPage.objects.create(
            title="Private Page",
            body="A page only for the student representative group.",
            visible_for=[fsr],
            depth=4,
            path="0001000200010002",
            is_public=False,
            author_visible=True,
        ),
        InformationPage.objects.create(
            title="Public Page",
            body="A page for everyone.",
            is_public=True,
            depth=4,
            path="0001000200010003",
            author_visible=False,
        ),
    ]


def setup_data():
    # settings.DEBUG = True
    # settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
    users = create_users()
    groups = create_groups(users)
    create_basic_page_structure()
    create_information_pages(groups)

    return {"users": users, "groups": groups}
