import json

import aioredis

from ..utils import get_redis_url
from ..websocket import BaseWebsocketPublisher


def make_channel_group_name(channel_id):
    return f"group_{channel_id}"


class RedisPubSubPublisher(BaseWebsocketPublisher):
    """Publisher using Redis PubSub functionnality."""

    async def publish(self, channel_id, renders, removals):
        """
        Publishes in Redis the renders and removals to the channel group
        corresponding to channel_id.

        See base class.
        """

        channel_group_name = make_channel_group_name(channel_id)
        message = {"renders": renders, "removals": removals}

        redis = aioredis.from_url(get_redis_url())
        await redis.publish(channel_group_name, json.dumps(message))
