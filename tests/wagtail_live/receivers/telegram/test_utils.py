import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from wagtail_live.receivers.telegram import (
    get_base_telegram_url,
    get_telegram_bot_token,
    get_telegram_webhook_url,
)
from wagtail_live.receivers.telegram.utils import format_url


@override_settings(TELEGRAM_BOT_TOKEN="telegram-token")
def test_get_telegram_bot_token():
    assert get_telegram_bot_token() == "telegram-token"


def test_get_telegram_bot_token_raises_error():
    expected_err = "You haven't specified a Telegram bot token in your settings."
    get_telegram_bot_token.cache_clear()

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_telegram_bot_token()


@override_settings(TELEGRAM_BOT_TOKEN="telegram-token")
def test_get_base_telegram_url():
    got = get_base_telegram_url()

    assert got == "https://api.telegram.org/bottelegram-token/"


@override_settings(TELEGRAM_BOT_TOKEN="telegram-token")
@override_settings(TELEGRAM_WEBHOOK_URL="www.webhook.com")
def test_get_telegram_webhook_url():
    got = get_telegram_webhook_url()

    assert got == "www.webhook.com/wagtail_live/telegram/events/telegram-token/"


@override_settings(TELEGRAM_BOT_TOKEN="telegram-token")
@override_settings(TELEGRAM_WEBHOOK_URL="www.webhook.com/")
def test_get_telegram_webhook_url_trailing_slash():
    get_telegram_webhook_url.cache_clear()
    got = get_telegram_webhook_url()

    assert got == "www.webhook.com/wagtail_live/telegram/events/telegram-token/"


def test_get_telegram_webhook_url_raises_error():
    expected_err = "You haven't specified a Telegram webhook URL in your settings."
    get_telegram_webhook_url.cache_clear()

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_telegram_webhook_url()


def test_format_url():
    assert format_url("www.example.com") == "//www.example.com"
    assert format_url("//www.example.com") == "//www.example.com"
    assert format_url("http://www.example.com") == "http://www.example.com"
    assert format_url("https://www.example.com") == "https://www.example.com"
