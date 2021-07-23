import channels.layers
from asgiref.sync import async_to_sync

from wagtail_live.publishers.websocket import BaseWebsocketsPublisher


class DjangoChannelsPublisher(BaseWebsocketsPublisher):
    """Django channels publisher."""

    def publish(self, channel_id, renders, removals):
        """See base class."""

        group_name = f"liveblog_{channel_id}"
        message = {
            "type": "new_update",
            "renders": renders,
            "removals": removals,
        }

        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message)
