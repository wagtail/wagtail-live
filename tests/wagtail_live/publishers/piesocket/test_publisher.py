import json

import pytest
import requests
from django.test import override_settings

from wagtail_live.publishers.piesocket.publisher import (
    PieSocketPublisher,
    headers,
    publish_url,
)
from wagtail_live.publishers.piesocket.utils import (
    get_piesocket_api_key,
    get_piesocket_secret,
)


class ResponseMock:
    def __init__(self, ok):
        self.ok = ok

        def ok(self):
            return self.ok


API_KEY = "api-key"
SECRET = "not-secret"


@pytest.fixture
def piesocket_overrides():
    get_piesocket_api_key.cache_clear()
    get_piesocket_secret.cache_clear()
    with override_settings(PIESOCKET_API_KEY=API_KEY, PIESOCKET_SECRET=SECRET):
        yield


@pytest.mark.usefixtures("piesocket_overrides")
def test_publisher(mocker):
    publisher = PieSocketPublisher()
    channel_id = "some-id"
    renders = removals = []
    mocker.patch.object(requests, "post", return_value=ResponseMock(ok=True))

    publisher.publish(channel_id, renders, removals)

    expected = json.dumps(
        {
            "key": API_KEY,
            "secret": SECRET,
            "channelId": channel_id,
            "message": {"renders": renders, "removals": removals},
        }
    )
    requests.post.assert_called_once_with(publish_url, headers=headers, data=expected)


@pytest.mark.usefixtures("piesocket_overrides")
def test_publisher_response_not_ok(mocker, caplog):
    publisher = PieSocketPublisher()
    channel_id = "some-id"
    renders = removals = []
    mocker.patch.object(requests, "post", return_value=ResponseMock(ok=False))

    publisher.publish(channel_id, renders, removals)

    assert caplog.messages[0] == "Failed publishing new update to PieSocket API."
