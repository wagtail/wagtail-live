import asyncio
import json

import pytest
from starlette.testclient import TestClient

from wagtail_live.publishers.redis import make_channel_group_name
from wagtail_live.publishers.starlette.app import BUS, app


@pytest.mark.asyncio
async def test_app(redis):
    channel_id = "test_channel"
    channel_group_name = make_channel_group_name(channel_id)
    message = {"renders": {}, "removals": []}

    assert BUS.pubsub.channels == {}

    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/channel/{channel_id}/") as websocket:
            # Ensure subscribtion
            while not BUS._running.is_set():
                await asyncio.sleep(0)
            assert BUS.pubsub.channels == {channel_group_name: BUS.handle_message}

            # Publish message to channel group
            response = await redis.publish(channel_group_name, json.dumps(message))

            # Ensure that the message has been received in the channel group.
            assert response == 1

            # Ensure that the message is received by websocket client.
            assert websocket.receive_json() == message

    # Ensure unsubscription
    assert BUS.pubsub.channels == {}
