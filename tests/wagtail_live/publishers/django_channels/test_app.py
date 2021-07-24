import json

import pytest
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import override_settings

from wagtail_live.publishers.django_channels import live_websocket_route


@pytest.mark.asyncio
@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
async def test_django_channels_app():
    # Initialize
    channel_layer = get_channel_layer()
    application = URLRouter(live_websocket_route)
    communicator = WebsocketCommunicator(application, "ws/channel/test/")

    # Ensure websocket channel is added to liveblog_test group
    # when the websocket connection opens.
    connected, subprotocol = await communicator.connect()
    assert connected

    groups = channel_layer.groups
    assert len(groups) == 1
    assert "liveblog_test" in groups
    assert len(groups["liveblog_test"]) == 1

    # Ensure new_update method is called when a message is sent to liveblog_test group.
    message = {"type": "new_update", "renders": {}, "removals": []}
    await channel_layer.group_send("liveblog_test", message)

    response = await communicator.receive_from()
    assert json.loads(response) == {"renders": {}, "removals": []}

    # Ensure websocket channel is discarded from liveblog_test group
    # when the websocket connection closes.
    await communicator.disconnect()
    assert channel_layer.groups == {}
