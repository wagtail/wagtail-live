from wagtail_live.models import LivePageMixin
from wagtail_live.publishers.websocket import BaseWebsocketPublisher
from wagtail_live.signals import live_page_update


def test_publish_called_on_new_live_page_update_signal(mocker):
    ws_publisher = BaseWebsocketPublisher()
    mocker.patch.object(ws_publisher, "publish", return_value=None)
    live_page_update.connect(ws_publisher)

    try:
        update = {"channel_id": "some-id", "renders": {}, "removals": []}
        live_page_update.send(sender=LivePageMixin, **update)
        ws_publisher.publish.assert_called_once_with(**update)

    finally:
        live_page_update.disconnect(ws_publisher)
