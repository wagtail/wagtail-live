"""Wagtail Live signals."""

import django.dispatch

from wagtail_live.publishers.websocket import BaseWebsocketPublisher
from wagtail_live.utils import get_live_publisher

live_page_update = django.dispatch.Signal()

live_publisher = get_live_publisher()

# Connect a listener to the live_page_update signal
# if the publisher defined uses the websockets technique
if issubclass(live_publisher, BaseWebsocketPublisher):
    live_page_update.connect(live_publisher())
