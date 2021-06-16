"""Wagtail Live publisher classes."""

from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View


class IntervalPollingPublisherView(View):
    """Interval polling Publisher. Class Based View.

    This class handles delivering new updates to the client side (Interval polling technique).
    It comprises 3 methods which correspond to the following steps:

    1- The client side initiates (shake) the communication by sending a POST request.
        The publisher acknowledges by sending relevant data to the client side.

    2- The client side asks if there are any updates by sending a HEAD request.
        If no updates are available, client side sleeps for the duration of the polling interval
        and repeats this step.

    3- If new updates are available, client side sends a GET request to get the new updates.
    """

    model = apps.get_model(settings.LIVE_APP, settings.LIVE_PAGE_MODEL)

    def post(self, request, channel_id, *args, **kwargs):
        """Initiates communication with client side and sends current live posts.

        Args:
            request (WSGIRequest):
                Client side's request
            channel_id (str):
                Id of the channel to get updates from.

        Returns:
            (JSONResponse) containing:
            - A list of the IDs of the current live posts for the page requested.
                Client side uses this list to keep track of live posts that have been deleted.

            - The duration of the polling interval.
                The user can set this parameter in his settings by doing so:
                POLLING_INTERVAL = (duration in ms)
                Defaults to 3000(ms).

            - Timestamp of the last update for the page requested.
                Client side uses this to know when new updates are available.

            (Http404) if a page corresponding to the channel_id given doesn't exist.
        """

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        return JsonResponse(
            {
                "livePosts": [live_post.id for live_post in live_page.live_posts],
                "lastUpdateTimestamp": live_page.last_update_timestamp,
                "pollingInterval": getattr(settings, "POLLING_INTERVAL", 3000),
            }
        )

    def head(self, request, channel_id, *args, **kwargs):
        """Sends last update timestamp for the page requested.

        Args:
            request (WSGIRequest):
                Client side's request
            channel_id (str):
                Id of the channel to get last update's timestamp from.

        Returns:
            (HttpResponse) containing the timestamp of the last update for the page requested.

            Client side checks if this value is greater than the last one received.
            In such case, the client side knows that new uopdates are available and sends a
            GET request.

            (Http404) if a page corresponding to the channel_id given doesn't exist.
        """

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        return HttpResponse(headers={"Last-Update-At": live_page.last_update_timestamp})

    def get(self, request, channel_id, *args, **kwargs):
        """Retrieves and sends new updates.

        Args:
            request (WSGIRequest):
                Client side's request sent along with the timestamp of the
                last update received.
            channel_id (str):
                Id of the channel to get last update's timestamp from.

        Returns:
            (JSONResponse) containing:
            - A dictionnary of the live posts updated since client side's last update timestamp.
                Keys represents IDs of the live posts edited and the values are the
                new content of those live posts.

            - A list of the IDs of the current live posts for the page requested.
                Client side compares this list to the one it has and remove the live posts
                whose IDs aren't in this new list.

            - Timestamp of the last update for the page requested.
                Client side uses this to know when new updates are available.

            (Http404) if a page corresponding to the channel_id given doesn't exist.
        """

        live_page = get_object_or_404(self.model, channel_id=channel_id)
        last_update_client = request.GET.get("last_update_ts")
        last_update_client = datetime.fromtimestamp(float(last_update_client))

        current_posts = []
        updated_posts = {}
        live_posts = live_page.live_posts
        for post in live_posts:
            post_id = post.id
            current_posts.append(post_id)

            created = post.value["created"]
            if created > last_update_client:  # This is a new post
                updated_posts[post_id] = post.render(context={"block_id": post_id})
                continue

            last_modified = post.value["modified"]
            if last_modified and last_modified > last_update_client:
                # This is an edited post
                updated_posts[post_id] = post.render(context={"block_id": post_id})

        return JsonResponse(
            {
                "updates": updated_posts,
                "currentPosts": current_posts,
                "lastUpdateTimestamp": live_page.last_update_timestamp,
            }
        )
