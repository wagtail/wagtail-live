"""Wagtail Live URLs."""

import logging

from django.core.exceptions import ImproperlyConfigured

from .exceptions import WebhookSetupError
from .utils import get_live_receiver, get_publisher

logger = logging.getLogger(__name__)

urlpatterns = []

try:
    publisher = get_publisher()
except ImproperlyConfigured:
    logger.error("No publisher defined.")
else:
    urlpatterns += publisher.get_urls()

live_receiver = get_live_receiver()
if live_receiver:
    try:
        urlpatterns += live_receiver.get_urls()
    except WebhookSetupError:
        logger.error("Webhook setup failed")
