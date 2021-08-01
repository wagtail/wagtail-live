import channels.layers
from asgiref.sync import async_to_sync
from django.test import override_settings

from wagtail_live.models import LivePageMixin
from wagtail_live.publishers.django_channels import DjangoChannelsPublisher
from wagtail_live.signals import live_page_update


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
def test_publish_new_update_on_live_page_update_signal():
    # Add 'test-channel' to live page group
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_add)("liveblog_some_id", "test-channel")

    # Connect publisher to live_page_update signal
    publisher = DjangoChannelsPublisher()
    live_page_update.connect(publisher)

    try:
        # Send live_page_update signal
        live_page_update.send(
            sender=LivePageMixin, channel_id="some_id", renders={}, removals=[]
        )

        # Ensure that the update is published i.e sent to live page group
        message = async_to_sync(channel_layer.receive)("test-channel")
        assert message == {"type": "update", "renders": {}, "removals": []}

    finally:
        live_page_update.disconnect(publisher)
        async_to_sync(channel_layer.group_discard)("liveblog_some_id", "test-channel")
