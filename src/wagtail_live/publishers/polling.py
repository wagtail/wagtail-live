import time
from datetime import datetime, timezone

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from wagtail_live.utils import get_polling_interval, get_polling_timeout

from .base import PollingPublisherMixin


class IntervalPollingPublisher(PollingPublisherMixin):
    """Interval polling Publisher. Class Based View.

    This class handles delivering new updates to the client side (Interval polling technique).
    It accepts 3 request methods (POST, HEAD and GET) which correspond to the following steps:

    1- The client side initiates (shake) the communication by sending a POST request.
        The publisher acknowledges by sending relevant data to the client side.

    2- The client side asks if there are any updates by sending a HEAD request.
        If no updates are available, client side sleeps for the duration of the polling interval
        and repeats this step.

    3- If new updates are available, client side sends a GET request to get the new updates.
    """

    url_name = "interval-polling"

    def post(self, request, channel_id, *args, **kwargs):
        """See base class."""

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        return JsonResponse(
            {
                "livePosts": [live_post.id for live_post in live_page.live_posts],
                "lastUpdateTimestamp": live_page.last_update_timestamp,
                "pollingInterval": get_polling_interval(),
            }
        )

    def head(self, request, channel_id, *args, **kwargs):
        """Sends the timestamp of the last update for the page requested.

        Args:
            request (HttpRequest):
                Client side's request
            channel_id (str):
                Id of the channel to get last update's timestamp from.

        Returns:
            (HttpResponse) containing the timestamp of the last update for the page requested.

            Client side checks if this value is greater than the last one received.
            In such case, the client side knows that new updates are available and sends a
            GET request to get those updates.

            (Http404) if a page corresponding to the channel_id given doesn't exist.
        """

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        response = JsonResponse(data={}, status=200)
        response["Last-Update-At"] = live_page.last_update_timestamp
        return response

    def get(self, request, channel_id, *args, **kwargs):
        """See base class."""

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        last_update_client = self.get_last_update_client_from_request(request=request)
        tz = timezone.utc if settings.USE_TZ else None
        updated_posts, current_posts = live_page.get_updates_since(
            last_update_ts=datetime.fromtimestamp(last_update_client, tz=tz),
        )

        return JsonResponse(
            {
                "updates": updated_posts,
                "currentPosts": current_posts,
                "lastUpdateTimestamp": live_page.last_update_timestamp,
            }
        )


class LongPollingPublisher(PollingPublisherMixin):
    """Long polling Publisher. Class Based View.

    This class handles delivering new updates to the client side (Long polling technique).
    It accepts 2 request methods (POST and GET) which correspond to the following steps:

    1- The client side initiates (shake) the communication by sending a POST request.
        The publisher acknowledges by sending relevant data to the client side.

    2- The client side asks new updates by sending a GET request.
        Server side keeps the connection open until a new update is available.
        In that case, updates are directly sent to client side.
        If the polling timeout duration is reached, it sends a response
        containing a timeOutReached parameter which indicates the client side
        that there aren't updates available.
    """

    url_name = "long-polling"

    def post(self, request, channel_id, *args, **kwargs):
        """See base class."""

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        return JsonResponse(
            {
                "livePosts": [live_post.id for live_post in live_page.live_posts],
                "lastUpdateTimestamp": live_page.last_update_timestamp,
            }
        )

    def get(self, request, channel_id, *args, **kwargs):
        """Sends updates when they are available as long as the polling timeout isn't reached.
        See base class.
        """

        last_update_client = self.get_last_update_client_from_request(request=request)
        polling_timeout = get_polling_timeout()
        starting_time = time.time()

        while time.time() - starting_time < polling_timeout:
            live_page = get_object_or_404(self.model, channel_id=channel_id)
            last_update_ts = live_page.last_update_timestamp
            if last_update_ts > last_update_client:
                tz = timezone.utc if settings.USE_TZ else None
                updated_posts, current_posts = live_page.get_updates_since(
                    last_update_ts=datetime.fromtimestamp(last_update_client, tz=tz),
                )

                return JsonResponse(
                    {
                        "updates": updated_posts,
                        "currentPosts": current_posts,
                        "lastUpdateTimestamp": last_update_ts,
                    }
                )

            # Maybe propose a setting so the user can define this value
            time.sleep(0.5)

        return JsonResponse({"timeOutReached": "Timeout duration reached."})
