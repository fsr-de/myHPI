import sys

import requests
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from myhpi.feed.models import NewsFeed, NewsFeedAccount, Post


def get_release(tag):
    r = requests.get(f"https://api.github.com/repos/fsr-de/myHPI/releases/tags/{tag}")
    r.raise_for_status()
    return r.json()


def publish_release_post(force_publish, tag=None):
    if tag is None:
        version = settings.MYHPI_VERSION
        tag = f"v{version}"
    release = get_release(tag)

    feed = NewsFeed.objects.first()
    if feed is None:
        print("No feed found, not publishing release post", file=sys.stderr)
        return

    existing_posts = Post.objects.filter(title=release["name"])
    if existing_posts.exists() and not force_publish:
        print(
            "Release post already exists, not publishing again. Use -f option to create a post anyway.",
            file=sys.stderr,
        )
        return

    account_id = settings.RELEASE_POST_ACCOUNT_ID
    if account_id is None:
        print("No account id found, not publishing release post", file=sys.stderr)
        return
    account = NewsFeedAccount.objects.filter(id=account_id).first()
    if account is None:
        print("No account found, not publishing release post", file=sys.stderr)
        return

    post = feed.add_child(
        instance=Post(
            title=release["name"],
            body=release["body"],
            post_account=account,
            visible_for=Group.objects.all(),
            is_public=True,
            first_published_at=release["published_at"],
        )
    )
    print(f"Published release post with id {post.id}", file=sys.stderr)


class Command(BaseCommand):
    help = "Creates a feed post for the latest release of myHPI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            "-f",
            action="store_true",
            help="Create a release post even if the release is already published.",
        )

        parser.add_argument(
            "--tag",
            "-t",
            type=str,
            help="Specify a tag to publish a release post for (defaults to currently installed version, typically latest tag).",
        )

    def handle(self, *args, **options):
        publish_release_post(options["force"], options["tag"])
