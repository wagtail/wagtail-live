from channels.layers import get_channel_layer

from wagtail_live.publishers.websocket import BaseWebsocketPublisher


class DjangoChannelsPublisher(BaseWebsocketPublisher):
    """Django channels publisher."""

    async def publish(self, channel_id, renders, removals):
        """Sends updates to the room group corresponding to channel_id."""

        channel_layer = get_channel_layer()
        group_name = f"liveblog_{channel_id}"
        message = {
            "type": "update",
            "renders": renders,
            "removals": removals,
        }

        await channel_layer.group_send(group_name, message)
