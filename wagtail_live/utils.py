"""Wagtail Live utils."""

import hmac
import re
from hashlib import sha256

from django.conf import settings
from wagtail.embeds.oembed_providers import all_providers


def get_live_receiver():
    """Retrieves the live receiver chosen.

    Returns:
        (BaseMessageReceiver) corresponding to the live receiver specified if found else None.
    """

    live_receiver = getattr(settings, "WAGTAIL_LIVE_RECEIVER", "")
    if live_receiver == "SlackEventsAPIReceiver":
        from wagtail_live.adapters.slack.receiver import SlackEventsAPIReceiver

        return SlackEventsAPIReceiver


def is_embed(text):
    """Checks if a text is a link to embed.

    Args:
        text (str): Text to check

    Returns:
        (bool) True if text corresponds to an embed link False else
    """

    for provider in all_providers:
        for url_pattern in provider.get("urls", []):
            # Somehow Slack links start with `<` and end with `>`.
            if bool(re.match(url_pattern, text)):
                return True

    return False


def sign_slack_request(content):
    """Signs content from a Slack request using the SLACK_SIGNING_SECRET as key."""

    hasher = hmac.new(str.encode(settings.SLACK_SIGNING_SECRET), digestmod=sha256)
    hasher.update(str.encode(content))
    return hasher.hexdigest()
