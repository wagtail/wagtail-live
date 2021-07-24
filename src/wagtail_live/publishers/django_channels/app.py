from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.urls import re_path


class DjangoChannelsApp(JsonWebsocketConsumer):
    """App/Consumer which handles websocket connections."""

    def connect(self):
        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        self.group_name = f"liveblog_{self.channel_id}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive_json(self, data=None):
        pass

    def new_update(self, event):
        """Receives messages from room group and send them to websocket."""

        self.send_json({"renders": event["renders"], "removals": event["removals"]})


live_websocket_route = [
    re_path(r"ws/channel/(?P<channel_id>\w+)/$", DjangoChannelsApp.as_asgi()),
]
