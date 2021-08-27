from django.test import override_settings

from tests.utils import reload_urlconf
from wagtail_live.exceptions import WebhookSetupError
from wagtail_live.receivers.telegram import TelegramWebhookReceiver


@override_settings(WAGTAIL_LIVE_PUBLISHER="")
def test_urls_no_publisher(caplog):
    reload_urlconf()

    assert (
        caplog.messages[0] == "You haven't specified a live publisher in your settings."
    )


@override_settings(
    WAGTAIL_LIVE_RECEIVER="wagtail_live.receivers.telegram.TelegramWebhookReceiver"
)
def test_urls_webhook_setup_error(caplog, mocker):
    mocker.patch.object(
        TelegramWebhookReceiver, "webhook_connection_set", return_value=False
    )
    mocker.patch.object(
        TelegramWebhookReceiver, "set_webhook", side_effect=WebhookSetupError
    )
    reload_urlconf()

    assert caplog.messages[0] == "Webhook setup failed"
