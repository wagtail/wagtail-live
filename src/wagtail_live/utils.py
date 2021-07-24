"""Wagtail Live utils"""

import re
from functools import lru_cache
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from wagtail.embeds.oembed_providers import all_providers

SUPPORTED_MIME_TYPES = ["png", "jpeg", "gif"]


def get_live_page_model():
    """Retrieves the live page model specified.

    Returns:
        (LivePageMixin) corresponding to the live page model specified.

    Raises:
        (ImproperlyConfigured) if no live page model is specified or the one
        specified doesn't inherit from wagtail_live.models.LivePageMixin.
    """

    from wagtail_live.models import LivePageMixin

    live_model = getattr(settings, "WAGTAIL_LIVE_PAGE_MODEL", "")
    if not live_model:
        raise ImproperlyConfigured(
            "You haven't specified a live page model in your settings."
        )

    dotted_path, model_name = live_model.rsplit(".", 1)
    module = import_module(dotted_path)
    model = getattr(module, model_name)

    if not issubclass(model, LivePageMixin):
        raise ImproperlyConfigured(
            "The live page model specified doesn't inherit from "
            + "wagtail_live.models.LivePageMixin."
        )

    return model


def get_live_receiver():
    """Retrieves the live receiver chosen.

    Returns:
        (BaseMessageReceiver) corresponding to the live receiver specified if found else None.

    Raises:
        (ImproperlyConfigured) if the receiver specified doesn't inherit from
        wagtail_live.receivers.BaseMessageReceiver.
    """

    from wagtail_live.receivers.base import BaseMessageReceiver

    live_receiver = getattr(settings, "WAGTAIL_LIVE_RECEIVER", "")
    if not live_receiver:
        # Assume live interface is used, in which case no additional setup is needed.
        return

    dotted_path, receiver_name = live_receiver.rsplit(".", 1)
    module = import_module(dotted_path)
    receiver = getattr(module, receiver_name)

    if not issubclass(receiver, BaseMessageReceiver):
        raise ImproperlyConfigured(
            f"The receiver {live_receiver} doesn't inherit from "
            + "wagtail_live.receivers.BaseMessageReceiver."
        )
    return receiver


def get_live_publisher():
    """Retrieves the live receiver chosen.

    Returns:
        (Publisher) corresponding to the live publisher specified.

    Raises:
        (ImproperlyConfigured) if no publisher class is specified.
    """

    live_publisher = getattr(settings, "WAGTAIL_LIVE_PUBLISHER", "")
    if not live_publisher:
        raise ImproperlyConfigured(
            "You haven't specified a publisher class in your settings."
        )

    dotted_path, publisher_name = live_publisher.rsplit(".", 1)
    module = import_module(dotted_path)
    publisher = getattr(module, publisher_name)

    return publisher


def get_polling_timeout():
    """Retrieves the duration for the polling timeout for the long polling technique.
    The user can set this parameter in his settings by doing so:
    WAGTAIL_LIVE_POLLING_TIMEOUT = (duration in seconds)
    Defaults to 60(seconds).

    Returns:
        (int) the duration of the polling timeout if defined else 60.
    """

    return getattr(settings, "WAGTAIL_LIVE_POLLING_TIMEOUT", 60)


def get_polling_interval():
    """Retrieves the duration of the polling interval for the interval polling technique.
    The user can set this parameter in his settings by doing so:
    WAGTAIL_LIVE_POLLING_INTERVAL = (duration in ms)
    Defaults to 3000(ms).

    Returns:
        (int) the duration of the polling interval if defined else 3000.
    """

    return getattr(settings, "WAGTAIL_LIVE_POLLING_INTERVAL", 3000)


@lru_cache(maxsize=None)
def is_embed(text):
    """Checks if a text is a link to embed.

    Args:
        text (str): Text to check

    Returns:
        (bool) True if text corresponds to an embed link False else
    """

    for provider in all_providers:
        for url_pattern in provider.get("urls", []):
            if bool(re.match(url_pattern, text)):
                return True

    return False
