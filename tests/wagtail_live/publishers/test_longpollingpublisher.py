import json
from datetime import datetime

import pytest
from django.test import override_settings
from django.urls import resolve

from tests.testapp.models import BlogPage
from tests.utils import reload_urlconf
from wagtail_live.publishers.polling import LongPollingPublisher, PollingPublisherMixin


@pytest.fixture(scope="class")
@override_settings(
    WAGTAIL_LIVE_PUBLISHER="wagtail_live.publishers.polling.LongPollingPublisher"
)
def reload_urls():
    reload_urlconf()
    resolved = resolve("/wagtail_live/get-updates/test_channel/")

    assert resolved.url_name == "long-polling"


@pytest.fixture
def live_page(blog_page_factory):
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "post-1",
                "value": {
                    "message_id": "1",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2022-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "post-2",
                "value": {
                    "message_id": "2",
                    "created": "2022-01-01T12:00:00",
                    "modified": "2022-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
            {
                "type": "live_post",
                "id": "post-3",
                "value": {
                    "message_id": "3",
                    "created": "2021-01-01T12:00:00",
                    "modified": None,
                    "show": True,
                    "content": [],
                },
            },
        ]
    )
    page = blog_page_factory(channel_id="test_channel", live_posts=live_posts)
    page.save_revision().publish()
    return page


def test_long_polling_publisher_instance():
    assert isinstance(LongPollingPublisher(), PollingPublisherMixin)


@pytest.mark.django_db
@pytest.mark.usefixtures("reload_urls")
class TestLongPolling:
    def test_post(self, live_page, client):
        response = client.post("/wagtail_live/get-updates/test_channel/")
        assert response.status_code == 200

        payload = response.json()
        assert payload["livePosts"] == ["post-1", "post-2", "post-3"]

        page = BlogPage.objects.get(channel_id="test_channel")
        assert payload["lastUpdateTimestamp"] == page.last_update_timestamp

    def test_post_bad_channel(self, blog_page_factory, client):
        blog_page_factory(channel_id="good_channel")
        response = client.post("/wagtail_live/get-updates/bad_channel/")

        assert response.status_code == 404

    def test_get(self, live_page, client):
        response = client.get(
            "/wagtail_live/get-updates/test_channel/",
            {"last_update_ts": datetime(2021, 2, 1).timestamp()},
        )
        assert response.status_code == 200

        payload = response.json()
        assert "post-1" in payload["updates"]
        assert "post-2" in payload["updates"]
        assert "post-3" not in payload["updates"]
        assert payload["currentPosts"] == ["post-3", "post-2", "post-1"]

        page = BlogPage.objects.get(channel_id="test_channel")
        assert payload["lastUpdateTimestamp"] == page.last_update_timestamp

    def test_get_bad_channel(self, blog_page_factory, client):
        blog_page_factory(channel_id="good_channel")
        response = client.get(
            "/wagtail_live/get-updates/bad_channel/",
            {"last_update_ts": datetime(2021, 2, 1).timestamp()},
        )
        assert response.status_code == 404

    @override_settings(WAGTAIL_LIVE_POLLING_TIMEOUT=1e-6)
    def test_get_timeout_reached(self, live_page, client):
        response = client.get(
            "/wagtail_live/get-updates/test_channel/",
            {"last_update_ts": live_page.last_update_timestamp + 5},
        )
        assert response.status_code == 200

        payload = response.json()
        assert payload["timeOutReached"] == "Timeout duration reached."
