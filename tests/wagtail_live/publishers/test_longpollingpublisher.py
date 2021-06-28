import json
from datetime import datetime

import pytest
from django.conf import settings
from django.urls import resolve

from tests.utils import reload_urlconf
from wagtail_live.publishers import LongPollingPublisher, PollingPublisherMixin


@pytest.fixture(scope="class")
def reload_urls():
    initial_value = getattr(settings, "WAGTAIL_LIVE_PUBLISHER", "")
    settings.WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.LongPollingPublisher"
    reload_urlconf()
    resolved = resolve("/wagtail_live/get-updates/test_channel/")
    assert resolved.url_name == "long-polling"
    settings.WAGTAIL_LIVE_PUBLISHER = initial_value


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
                    "modified": None,
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
                    "modified": "2022-01-01T12:00:00",
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
        assert payload["lastUpdateTimestamp"] == live_page.last_update_timestamp

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
        assert "post-2" in payload["updates"]
        assert "post-3" in payload["updates"]
        assert "post-1" not in payload["updates"]
        assert payload["currentPosts"] == ["post-1", "post-2", "post-3"]
        assert payload["lastUpdateTimestamp"] == live_page.last_update_timestamp

    def test_get_bad_channel(self, blog_page_factory, client):
        blog_page_factory(channel_id="good_channel")
        response = client.get(
            "/wagtail_live/get-updates/bad_channel/",
            {"last_update_ts": datetime(2021, 2, 1).timestamp()},
        )
        assert response.status_code == 404

    def test_get_timeout_reached(self, live_page, client, settings):
        settings.WAGTAIL_LIVE_POLLING_TIMEOUT = 1e-6
        response = client.get(
            "/wagtail_live/get-updates/test_channel/",
            {"last_update_ts": live_page.last_update_timestamp + 5},
        )
        assert response.status_code == 200

        payload = response.json()
        assert payload["timeOutReached"] == "Timeout duration reached."
