import asyncio
from collections import defaultdict

import aioredis

from ..utils import get_redis_url


class RedisBus:
    """
    Class providing an event bus based on Redis PubSub.

    A channel group is created for each live page.

    Users viewing the page in live are added to that channel group.

    When a live page is updated, a message is sent to its corresponding
    channel group. The message sent contains the renders and the removals
    i.e the new updates of the page.

    The message is then broadcasted to users that have subscribed to that
    channel group.

    Attributes:
        pubsub (PubSub):
            Redis PubSub class which allows to do pub/sub operations.
        broadcast (callable):
            The function to use when broadcasting a message to clients.
        channel_groups (dict):
            Maps a channel group to the connections that have subscribed to it.

    """

    def __init__(self, url, broadcast):
        redis = aioredis.from_url(get_redis_url(), decode_responses=True)
        self.pubsub = redis.pubsub(ignore_subscribe_messages=True)
        self.broadcast = broadcast
        self.channel_groups = defaultdict(set)
        # Tracks when the bus starts running i.e on the first connection.
        self._running = None

    async def run(self):
        """Retrieves messages from Redis and dispatches them as long as the server is running."""

        # We will have an error if we try to run the bus if we haven't
        # subscribed to any channel yet.
        # Therefore, wait for the bus to start running before calling pubsub.run.
        self._running = asyncio.Event()
        await self._running.wait()
        await self.pubsub.run()

    def _set_running(self):
        if self._running is not None and not self._running.is_set():
            self._running.set()

    def get_channel_group_subscribers(self, channel_group_name):
        """
        Retrieves the connections that have subscribed to channel_group_name.

        Args:
            channel_group_name (str):
                The channel group to find subscribers for.

        Returns:
            Set: Connections/users that have subscribed to the given channel group.
        """

        return self.channel_groups[channel_group_name]

    def handle_message(self, message):
        """
        Callback called when a message is published on a channel.

        Retrieves the connections that should receive the message and
        spawns a task to broadcast them the message.

        Args:
            message (str): The message published on Redis.
        """

        connections = self.get_channel_group_subscribers(message["channel"])
        asyncio.create_task(self.broadcast(message["data"], connections))

    async def subscribe(self, channel_group_name, ws_connection):
        """
        Subscribes a connection to a channel group.

        Args:
            channel_group_name (str):
                Channel group to subscribe to
            ws_connection (*):
                The websocket or connection instance to add to the channel_group subscribers.
                It must have a method to send messages.
        """

        # Subscribe to this channel group in Redis if not done yet.
        if not self.get_channel_group_subscribers(channel_group_name):
            # Passing parameters as `channel=handler` to the pubsub.subscribe method
            # has the effect to call `handler` whenever a message is published on `channel`.
            await self.pubsub.subscribe(**{channel_group_name: self.handle_message})

        self.channel_groups[channel_group_name].add(ws_connection)
        self._set_running()

    async def unsubscribe(self, channel_group_name, ws_connection):
        """
        Unsubscribes a connection from a channel group.

        Args:
            channel_group_name (str):
                Channel group to unsubscribe from.
            ws_connection (*):
                The websocket or connection instance to remove from the channel_group subscribers.

        """

        self.channel_groups[channel_group_name].remove(ws_connection)

        # Unsubscribe from this channel_group in Redis if no more
        # connections are subscribed to it.
        if not self.get_channel_group_subscribers(channel_group_name):
            await self.pubsub.unsubscribe(channel_group_name)
            del self.channel_groups[channel_group_name]
