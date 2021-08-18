import asyncio
import json

import pytest
import websockets

from tests.wagtail_live.publishers.conftest import wait_for_message
from wagtail_live.publishers.redis import make_channel_group_name
from wagtail_live.publishers.websockets import app


@pytest.mark.asyncio
async def test_app(redis):
    channel_id = "test_channel"
    channel_group_name = make_channel_group_name(channel_id)
    # Use default values for port and host
    uri = f"ws://localhost:8765/ws/channel/{channel_id}/"
    message = json.dumps({"renders": {}, "removals": []})

    pubsub = app.bus.pubsub
    task = asyncio.create_task(app())

    # Ensure server is running
    while app.bus._running is None:
        await asyncio.sleep(0)
    assert pubsub.channels == {}

    async with websockets.connect(uri) as websocket:
        # Ensure subscribtion
        while not app.bus._running.is_set():
            await asyncio.sleep(0)
        assert pubsub.channels == {channel_group_name: app.bus.handle_message}

        await redis.publish(channel_group_name, message)

        assert await websocket.recv() == message

        task.cancel()

    await wait_for_message(pubsub)
    assert pubsub.channels == {}
