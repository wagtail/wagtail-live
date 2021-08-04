import pytest

from wagtail_live.publishers.redis import RedisPubSubPublisher, make_channel_group_name

from ..conftest import wait_for_message


def test_make_channel_group_name():
    assert make_channel_group_name("test_channel") == "group_test_channel"


@pytest.mark.asyncio
async def test_redis_publish(redis):
    pubsub = redis.pubsub()
    publisher = RedisPubSubPublisher()
    group = make_channel_group_name("test_channel")

    await pubsub.subscribe(group)

    await publisher.publish("test_channel", {}, [])

    message = await wait_for_message(pubsub)

    assert message == {
        "type": "message",
        "pattern": None,
        "channel": "group_test_channel",
        "data": '{"renders": {}, "removals": []}',
    }
