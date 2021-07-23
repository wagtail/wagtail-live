"""Wagtail Live signals."""

import django.dispatch

from .utils import get_updates_publisher

live_page_update = django.dispatch.Signal()

updates_publisher = get_updates_publisher()

# Connect a listener to the live_page_update signal
# if the publisher defined uses the websockets technique
if updates_publisher:
    live_page_update.connect(updates_publisher)
