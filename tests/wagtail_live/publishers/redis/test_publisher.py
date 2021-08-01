import pytest

from wagtail_live.publishers.redis import RedisPubSubPublisher, make_channel_group_name
from wagtail_live.publishers.redis import publisher as r_publisher

from ..conftest import wait_for_message


def test_make_channel_group_name():
    assert make_channel_group_name("test_channel") == "group_test_channel"


@pytest.mark.asyncio
async def test_redis_publish(redis):
    pubsub = redis.pubsub()
    group = make_channel_group_name("test_channel")

    await pubsub.subscribe(group)

    await r_publisher.redis_publish(group, "hey")

    message = await wait_for_message(pubsub)
    assert message == {
        "type": "message",
        "pattern": None,
        "channel": "group_test_channel",
        "data": '"hey"',
    }


def test_redis_publisher(mocker):
    publisher = RedisPubSubPublisher()
    mocker.patch.object(r_publisher, "redis_publish")
    publisher.publish("test_channel", {}, [])

    r_publisher.redis_publish.assert_called_once_with(
        "group_test_channel", {"renders": {}, "removals": []}
    )
