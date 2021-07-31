from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.urls import re_path


class DjangoChannelsApp(AsyncJsonWebsocketConsumer):
    """App/Consumer which handles websocket connections."""

    async def connect(self):
        """Adds websocket channel to room group."""

        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        self.group_name = f"liveblog_{self.channel_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Discards websocket channel from room group."""

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def update(self, event):
        """Receives messages from room group and sends them to websocket client."""

        await self.send_json(
            {"renders": event["renders"], "removals": event["removals"]}
        )


live_websocket_route = [
    re_path(r"ws/channel/(?P<channel_id>\w+)/$", DjangoChannelsApp.as_asgi()),
]
