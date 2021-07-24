from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.urls import re_path


class DjangoChannelsApp(JsonWebsocketConsumer):
    """App/Consumer which handles websocket connections."""

    def connect(self):
        """Adds websocket channel to room group."""

        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        self.group_name = f"liveblog_{self.channel_id}"

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        """Discards websocket channel from room group."""

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def new_update(self, event):
        """Receives messages from room group and sends them to websocket client."""

        self.send_json({"renders": event["renders"], "removals": event["removals"]})


live_websocket_route = [
    re_path(r"ws/channel/(?P<channel_id>\w+)/$", DjangoChannelsApp.as_asgi()),
]
