import json

import aioredis
from asgiref.sync import async_to_sync

from ..utils import get_redis_url
from ..websocket import BaseWebsocketPublisher


def make_channel_group_name(channel_id):
    return f"group_{channel_id}"


async def redis_publish(channel_group_name, message):
    """
    Publishes a message to the given channel in Redis.

    Args:
        channel_group_name (str):
            Channel to publish the message to.
        message (*):
            Message to publish.
    """

    redis = aioredis.from_url(get_redis_url())
    await redis.publish(channel_group_name, json.dumps(message))


class RedisPubSubPublisher(BaseWebsocketPublisher):
    """Publisher using Redis PubSub functionnality."""

    def publish(self, channel_id, renders, removals):
        """
        Publishes in Redis the renders and removals to the channel group
        corresponding to channel_id.

        See base class.
        """

        channel_group_name = make_channel_group_name(channel_id)
        message = {"renders": renders, "removals": removals}

        async_to_sync(redis_publish)(channel_group_name, message)
