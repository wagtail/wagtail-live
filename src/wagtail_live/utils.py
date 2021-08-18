"""Wagtail Live utils"""

import re
from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from wagtail.embeds.oembed_providers import all_providers

SUPPORTED_MIME_TYPES = ["png", "jpeg", "gif"]


def get_live_page_model():
    """
    Retrieves the live page model specified in user's settings.

    Returns:
        LivePageMixin:
            The live page model specified.

    Raises:
        ImproperlyConfigured: if no live page model is specified or
            the one specified doesn't inherit from `wagtail_live.models.LivePageMixin`.
        ImportError: if the live page model class couldn't be loaded.
    """

    from wagtail_live.models import LivePageMixin

    live_model = getattr(settings, "WAGTAIL_LIVE_PAGE_MODEL", "")
    if not live_model:
        raise ImproperlyConfigured(
            "You haven't specified a live page model in your settings."
        )

    model = import_string(live_model)

    if not issubclass(model, LivePageMixin):
        raise ImproperlyConfigured(
            "The live page model specified doesn't inherit from wagtail_live.models.LivePageMixin."
        )

    return model


def get_live_receiver():
    """
    Retrieves the live receiver specified in user's settings.

    Returns:
        BaseMessageReceiver: The live receiver specified if found else `None`.

    Raises:
        ImproperlyConfigured: if the receiver specified doesn't inherit from
            `wagtail_live.receivers.BaseMessageReceiver`.
        ImportError: if the receiver class couldn't be loaded.
    """

    from wagtail_live.receivers.base import BaseMessageReceiver

    live_receiver = getattr(settings, "WAGTAIL_LIVE_RECEIVER", "")
    if not live_receiver:
        # Assume live interface is used, in which case no additional setup is needed.
        return

    receiver = import_string(live_receiver)

    if not issubclass(receiver, BaseMessageReceiver):
        raise ImproperlyConfigured(
            f"The receiver {live_receiver} doesn't inherit from"
            + "wagtail_live.receivers.BaseMessageReceiver."
        )
    return receiver


def get_live_publisher():
    """
    Retrieves the live publisher specified in user's settings.

    Returns:
        Publisher: The live publisher specified.

    Raises:
        ImproperlyConfigured: if no publisher class is specified in settings.
        ImportError: if the publisher class couldn't be loaded.
    """

    live_publisher = getattr(settings, "WAGTAIL_LIVE_PUBLISHER", "")
    if not live_publisher:
        raise ImproperlyConfigured(
            "You haven't specified a publisher class in your settings."
        )

    return import_string(live_publisher)


def get_polling_timeout():
    """
    Retrieves the duration of the polling timeout for the long polling technique.

    The user can set this parameter in his settings by doing so:
    ```python
    WAGTAIL_LIVE_POLLING_TIMEOUT = (duration in seconds)
    ```

    The default value is 60 seconds.

    Returns:
        int: The duration of the polling timeout if defined else 60.
    """

    return getattr(settings, "WAGTAIL_LIVE_POLLING_TIMEOUT", 60)


def get_polling_interval():
    """
    Retrieves the duration of the polling interval for the interval polling technique.

    The user can set this parameter in his settings by doing so:
    ```python
    WAGTAIL_LIVE_POLLING_INTERVAL = (duration in ms)
    ```
    The default value is 3000 milliseconds.

    Returns:
        int: the duration of the polling interval if defined else 3000.
    """

    return getattr(settings, "WAGTAIL_LIVE_POLLING_INTERVAL", 3000)


@lru_cache(maxsize=None)
def is_embed(text):
    """
    Checks if a text is a link to embed.

    Args:
        text (str): Text to check

    Returns:
        bool:
        - `True` if text corresponds to an embed link.
        - `False` else.
    """

    for provider in all_providers:
        for url_pattern in provider.get("urls", []):
            if bool(re.match(url_pattern, text)):
                return True

    return False
