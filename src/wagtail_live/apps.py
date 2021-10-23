from django.apps import AppConfig


class WagtailLiveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wagtail_live"

    def ready(self):
        from wagtail_live.publishers.websocket import BaseWebsocketPublisher
        from wagtail_live.utils import get_live_publisher

        live_publisher = get_live_publisher()

        # Connect a listener to the live_page_update signal
        # if the publisher defined uses the websockets technique
        if issubclass(live_publisher, BaseWebsocketPublisher):
            from wagtail_live.signals import live_page_update

            # Set`weak=False` to avoid the publisher being garbage collected.
            # See:
            # https://docs.djangoproject.com/en/3.2/topics/signals/#django.dispatch.Signal.connect
            live_page_update.connect(
                live_publisher(), weak=False, dispatch_uid="live_publisher"
            )
