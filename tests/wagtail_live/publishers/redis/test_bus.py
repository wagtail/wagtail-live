import asyncio

import pytest

from wagtail_live.publishers.redis import RedisBus, make_channel_group_name
from wagtail_live.publishers.utils import get_redis_url

from ..conftest import wait_for_message

count = 0
_message = _recipients = None


async def broadcast(message, recipients):
    global count, _message, _recipients
    count += 1
    _message, _recipients = message, recipients


@pytest.fixture
def bus():
    return RedisBus(get_redis_url(), broadcast)


@pytest.mark.asyncio
async def test_pubsub(bus, redis):
    global count, _message, _recipients
    channel_group_name = make_channel_group_name("test_channel")
    other_channel_group_name = make_channel_group_name("other_channel")
    ws_1, ws_2, ws_3 = "ws_1", "ws_2", "ws_3"

    await bus.subscribe(channel_group_name, ws_1)
    await bus.subscribe(channel_group_name, ws_2)

    await bus.subscribe(other_channel_group_name, ws_3)

    assert bus.get_channel_group_subscribers(channel_group_name) == {ws_1, ws_2}
    assert bus.pubsub.channels == {
        channel_group_name: bus.handle_message,
        other_channel_group_name: bus.handle_message,
    }

    # Ensure that when a message is published in a channel group,
    # it is broadcasted to websocket connections that have subscribed to that channel group.
    await redis.publish(channel_group_name, "hey")
    await wait_for_message(bus.pubsub)
    assert count == 1
    assert _message == "hey"
    assert _recipients == {ws_1, ws_2}

    await bus.unsubscribe(other_channel_group_name, ws_3)
    assert bus.get_channel_group_subscribers(other_channel_group_name) == set()

    await wait_for_message(bus.pubsub)
    assert bus.pubsub.channels == {channel_group_name: bus.handle_message}

    await bus.unsubscribe(channel_group_name, ws_1)
    await bus.unsubscribe(channel_group_name, ws_2)
    await wait_for_message(bus.pubsub)
    assert bus.pubsub.channels == {}

    # Reset values
    count = 0
    _message = _recipients = None


@pytest.mark.asyncio
async def test_run(bus, redis):
    global count, _message, _recipients
    assert bus._running is None

    asyncio.create_task(bus.run())

    # Give a chance to the bus task to run
    await asyncio.sleep(0)
    assert not bus._running.is_set()

    channel_group_name = make_channel_group_name("test_channel")
    ws_connection = "ws_connection"
    await bus.subscribe(channel_group_name, ws_connection)
    assert bus._running.is_set()

    await redis.publish(channel_group_name, "hey")

    # Give a chance to the bus task to receive the message
    await asyncio.sleep(1e-3)
    assert count == 1
    assert _message == "hey"
    assert _recipients == {ws_connection}

    await bus.unsubscribe(channel_group_name, ws_connection)

    # Reset values
    count = 0
    _message = _recipients = None
