import re
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from wagtail.embeds.oembed_providers import all_providers

from .models import LivePageMixin


def get_live_page_model():
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


def get_publisher():
    live_publisher = getattr(settings, "WAGTAIL_LIVE_PUBLISHER", "")
    if not live_publisher:
        raise ImproperlyConfigured(
            "You haven't specified a publisher class in your settings."
        )

    dotted_path, publisher_name = live_publisher.rsplit(".", 1)
    module = import_module(dotted_path)
    publisher = getattr(module, publisher_name)

    return publisher


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
