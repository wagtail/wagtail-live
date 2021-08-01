import asyncio

import websockets

from ..redis import RedisBus, make_channel_group_name
from ..utils import get_live_server_host, get_live_server_port, get_redis_url


# Define the broadcast method to be used by the bus.
async def broadcast(message, recipients):
    await asyncio.wait([ws.send(message) for ws in recipients])


class WebsocketsPublisherApp:
    bus = RedisBus(url=get_redis_url(), broadcast=broadcast)

    async def __call__(self):
        """Called once per session."""

        host = get_live_server_host()
        port = get_live_server_port()
        async with websockets.serve(self.handler, host, port):
            await self.bus.run()  # Run the bus forever

    async def handler(self, websocket, path):
        """
        Called once per new connection.

        Adds/removes the websocket connection to/from the channel group
        corresponding to the channel id found in the request's path.
        """

        channel_id = path.split("/")[-2]
        channel_name = make_channel_group_name(channel_id)

        await self.bus.subscribe(channel_name, websocket)

        try:
            await websocket.wait_closed()

        finally:
            await self.bus.unsubscribe(channel_name, websocket)


app = WebsocketsPublisherApp()
