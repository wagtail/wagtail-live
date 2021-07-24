import sys
from importlib import reload

from django.test import override_settings


def test_live_page_update_signal_receivers():
    from wagtail_live.signals import live_page_update

    assert len(live_page_update.receivers) == 0


@override_settings(
    WAGTAIL_LIVE_PUBLISHER="tests.testapp.publishers.DummyWebsocketPublisher"
)
def test_live_page_update_signal_receivers_websocket():
    # Reload module so the settings override takes effect.
    reload(sys.modules["wagtail_live.signals"])

    from wagtail_live.signals import live_page_update

    assert len(live_page_update.receivers) == 1
