"""Wagtail Live URLs."""

import logging

from .exceptions import WebhookSetupError
from .utils import get_live_receiver

logger = logging.getLogger(__name__)


urlpatterns = []


live_receiver = get_live_receiver()
if live_receiver:
    try:
        urlpatterns += live_receiver.get_urls()
    except WebhookSetupError:
        logger.error("Webhook setup failed")
