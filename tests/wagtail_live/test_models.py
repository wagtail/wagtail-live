import json

import pytest


@pytest.mark.django_db
def test_blog_page_update_live_posts_creates_revision(blog_page_factory):
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "743fbd4d-929a-4b85-8f30-93cb19d6a933",
                "value": {
                    "message_id": "some_message_id",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            }
        ]
    )
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    assert page.revisions.count() == 0
    page.delete_live_post("743fbd4d-929a-4b85-8f30-93cb19d6a933")
    assert page.revisions.count() == 1
