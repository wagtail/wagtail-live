"""Wagtail Live URLs."""

import logging

from django.core.exceptions import ImproperlyConfigured

from .exceptions import WebhookSetupError
from .utils import get_live_publisher, get_live_receiver

logger = logging.getLogger(__name__)

urlpatterns = []

try:
    live_publisher = get_live_publisher()
except ImproperlyConfigured as err:
    logger.error(f"{err}")
else:
    urlpatterns += live_publisher.get_urls()

live_receiver = get_live_receiver()
if live_receiver:
    try:
        urlpatterns += live_receiver.get_urls()
    except WebhookSetupError:
        logger.error("Webhook setup failed")
