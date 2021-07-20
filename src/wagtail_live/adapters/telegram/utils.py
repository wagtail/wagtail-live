from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@lru_cache(maxsize=1)
def get_telegram_bot_token():
    """Retrieves user's telegram bot token.

    Returns:
        (str) telegram bot token.

    Raises:
        (ImproperlyConfigured) if the telegram bot token isn't specified in settings.
    """

    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        raise ImproperlyConfigured(
            "Specify TELEGRAM_BOT_TOKEN if you intend to use Telegram as input source."
        )
    return bot_token


@lru_cache(maxsize=1)
def get_telegram_webhook_url():
    """Retrieves the webhook url which Telegram sends new updates to.

    Returns:
        (str) a URL.

    Raises:
        (ImproperlyConfigured) if the telegram webhook url isn't specified in settings.
    """

    base_webhook_url = getattr(settings, "TELEGRAM_WEBHOOK_URL", "")
    if not base_webhook_url:
        raise ImproperlyConfigured(
            "Specify TELEGRAM_WEBHOOK_URL if you intend to use Telegram as input source."
        )

    if base_webhook_url.endswith("/"):
        base_webhook_url = base_webhook_url[:-1]

    return (
        f"{base_webhook_url}/wagtail_live/telegram/events/{get_telegram_bot_token()}/"
    )


@lru_cache(maxsize=1)
def get_base_telegram_url():
    """Returns the base URL to use when calling Telegram's API."""

    return f"https://api.telegram.org/bot{get_telegram_bot_token()}/"
