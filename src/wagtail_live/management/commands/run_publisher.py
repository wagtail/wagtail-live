from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Run a separate server for Wagtail Live publishers."

    def add_arguments(self, parser):
        parser.add_argument("publisher", nargs="+", type=str)

    def handle(self, *args, **options):
        publisher = options["publisher"][0]
        if publisher == "websockets":
            import asyncio

            from wagtail_live.publishers.websockets import app

            asyncio.run(app())

        elif publisher == "starlette":
            import uvicorn

            from wagtail_live.publishers.starlette import app
            from wagtail_live.publishers.utils import (
                get_live_server_host,
                get_live_server_port,
            )

            host, port = get_live_server_host(), get_live_server_port()

            uvicorn.run(app, host=host, port=port)

        else:
            raise CommandError('Publisher "%s" does not exist' % publisher)
