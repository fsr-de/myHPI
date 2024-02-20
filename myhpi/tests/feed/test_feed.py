from django.conf import settings

from myhpi.feed.models import NewsFeed, Post, NewsFeedAccount
from myhpi.tests.core.utils import MyHPIPageTestCase


class FeedTest(MyHPIPageTestCase):
    def setUp(self):
        super().setUp()

        self.feed = self.root_page.add_child(
            instance=NewsFeed(
                title="Feed",
                slug="feed",
                visible_for=[self.test_data["groups"][0]],
                is_public=False,
            )
        )

        self.post_account = NewsFeedAccount.objects.create(
            post_key="SECRET_POST_KEY",
            name="Test Post Account",
        )

    def test_post_to_feed(self):
        response = self.client.post(
            "/post",
            data={
                "title": "Test Post",
                "body": "This is a test post.",
            },
            content_type="application/json",
            HTTP_X_API_KEY="SECRET_POST_KEY",
        )

        self.assertEqual(response.status_code, 200)
        post_id = response.content.decode("utf-8")
        post = Post.objects.get(id=post_id)
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.get_parent().specific, self.feed)

    def test_post_to_feed_unauthorized(self):
        response = self.client.post(
            "/post",
            data={
                "title": "Test Post",
                "body": "This is a test post.",
            },
            content_type="application/json",
            HTTP_X_API_KEY="INVALID_POST_KEY",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_truncation(self):
        response = self.client.post(
            "/post",
            data={
                "title": "Test Post",
                "body": "A" * 1000,
            },
            content_type="application/json",
            HTTP_X_API_KEY="SECRET_POST_KEY",
        )

        self.assertEqual(response.status_code, 200)

        # Query feed and check if the post is truncated
        self.sign_in_as_student()
        response = self.client.get(self.feed.url)
        self.assertContains(
            response, "A" * (settings.FEED_TRUNCATE_LIMIT - 1)
        )  # -1 because of the ellipsis
        self.assertNotContains(response, "A" * (settings.FEED_TRUNCATE_LIMIT + 1))
