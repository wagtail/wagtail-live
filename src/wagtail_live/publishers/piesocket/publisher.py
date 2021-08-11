import json
import logging

import requests

from wagtail_live.publishers.websocket import BaseWebsocketPublisher

from .utils import get_piesocket_api_key, get_piesocket_secret

logger = logging.getLogger(__name__)

publish_url = "https://www.piesocket.com/api/publish"
headers = {"Content-Type": "application/json"}


class PieSocketPublisher(BaseWebsocketPublisher):
    """PieSocket publisher."""

    def publish(self, channel_id, renders, removals):
        """See base class."""

        payload = json.dumps(
            {
                "key": get_piesocket_api_key(),
                "secret": get_piesocket_secret(),
                "channelId": channel_id,
                "message": {"renders": renders, "removals": removals},
            }
        )

        response = requests.post(publish_url, headers=headers, data=payload)
        if not response.ok:
            logger.error("Failed publishing new update to PieSocket API.")
