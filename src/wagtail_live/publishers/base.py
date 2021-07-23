"""Wagtail Live publisher classes."""


from functools import cached_property

from django.urls import path
from django.views import View

from wagtail_live.utils import get_live_page_model


class PollingPublisherMixin(View):
    """A mixin for publishers using the polling technique.

    Attributes:
        url_path (str):
            Path of the URL used by client side to fetch new updates.
        url_name (str):
            Name of the URL for reversing/resolving.
    """

    url_path = "get-updates/<str:channel_id>/"
    url_name = ""

    @cached_property
    def model(self):
        """Retrieves the live model defined."""

        return get_live_page_model()

    @classmethod
    def get_urls(cls):
        """Retrieves the URLs client side uses to fetch updates."""

        return [
            path(cls.url_path, cls.as_view(), name=cls.url_name),
        ]

    @staticmethod
    def get_last_update_client_from_request(request):
        """Retrieves the timestamp of the last update received
        in the client side.

        Args:
            request (HttpRequest): client side request

        Returns:
            (float) timestamp of the last update received in the client side.
        """

        return float(request.GET.get("last_update_ts"))

    def post(self, request, channel_id, *args, **kwargs):
        """Initiates communication with client side and sends current live posts.

        Args:
            request (HttpRequest):
                Client side's request
            channel_id (str):
                Id of the channel to get updates from.

        Returns:
            (JSONResponse) containing:
            - A list of the IDs of the current live posts for the page requested.
                Client side uses this list to keep track of live posts that have been deleted.

            - Timestamp of the last update for the page requested.
                Client side uses this to know when new updates are available.

            - The duration of the polling interval for interval polling.

            (Http404) if a page corresponding to the channel_id given doesn't exist.
        """

        raise NotImplementedError

    def get(self, request, channel_id, *args, **kwargs):
        """Retrieves and sends new updates.

        Args:
            request (HttpRequest):
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

            (Http404) if a page corresponding to the channel_id given doesn't exist.
        """

        raise NotImplementedError
