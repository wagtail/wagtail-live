from django.apps import apps
from django.test import override_settings

from wagtail_live.signals import live_page_update


def test_live_page_update_signal_receivers():
    assert len(live_page_update.receivers) == 0


@override_settings(
    WAGTAIL_LIVE_PUBLISHER="tests.testapp.publishers.DummyWebsocketPublisher"
)
def test_live_page_update_signal_receivers_websocket():
    app_config = apps.get_app_config("wagtail_live")
    # Fails with Django 2.
    # Our ready method isn't called but Django's.
    app_config.ready()

    try:
        # Receiver should be connected, no IndexError
        receiver = live_page_update.receivers[0]
    finally:
        live_page_update.disconnect(receiver)
