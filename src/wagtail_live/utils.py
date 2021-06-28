"""Wagtail Live utils"""

from importlib import import_module
from typing import Optional, Type

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from wagtail_live.receivers import BaseMessageReceiver


def get_live_receiver() -> Optional[Type[BaseMessageReceiver]]:
    """Retrieves the live receiver chosen.

    Returns:
        (BaseMessageReceiver) corresponding to the live receiver specified if found else None.
    """

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
