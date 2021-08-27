from functools import lru_cache

from wagtail_live.utils import get_setting_or_raise


@lru_cache(maxsize=1)
def get_telegram_bot_token():
    """
    Retrieves user's telegram bot token.

    Returns:
        str: telegram bot token.

    Raises:
        ImproperlyConfigured: if the telegram bot token isn't specified in settings.
    """

    return get_setting_or_raise("TELEGRAM_BOT_TOKEN", "Telegram bot token")


@lru_cache(maxsize=1)
def get_telegram_webhook_url():
    """
    Retrieves the webhook url which Telegram sends new updates to.

    Returns:
        str: a URL.

    Raises:
        ImproperlyConfigured: if the telegram webhook url isn't specified in settings.
    """

    base_webhook_url = get_setting_or_raise(
        "TELEGRAM_WEBHOOK_URL", "Telegram webhook URL"
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


def format_url(url):
    """Fixes telegram url format"""

    # Prevent e.g. www.example.com from being interpreted as relative url
    if not url.startswith("http") and not url.startswith("//"):
        url = f"//{url}"

    return url
