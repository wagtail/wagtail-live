# How to write a websocket publisher

This guide shows how to write a publisher following the websocket protocol.

There are three ways to add a websocket publisher to Wagtail Live:

1. The classical way to add websocket support to a Django project which is using [Django channels](https://channels.readthedocs.io/en/stable/).
    
    Wagtail live already ships with a `DjangoChannelsPublisher`.

2. Use a hosted websocket solution.
    
    Examples: [Pusher](https://pusher.com/), [PieSocket](https://www.piesocket.com/), [Ably](https://ably.com/).

3. Deploy a separate server based on a framework or library that supports websocket.

    Examples: [Starlette](https://github.com/encode/starlette), [Websockets](https://github.com/aaugustin/websockets), [Tornado](https://www.tornadoweb.org/en/stable/).

In this guide we will see how to add a websocket publisher using either a hosted third-party solution or by deploying a separate server. Here are the steps to follow for both methods:

1. Inherit from [`BaseWebsocketPublisher`](https://wagtail.github.io/wagtail-live/reference/publishers/base_websocket_publisher/) and implement the `publish` method. This method handles publishing updates to websocket clients.

2. Add client side logic.


## Implement `publish` method

### Hosted websocket solutions

We have to check the third-party service's documentation to implement the `publish` method for hosted websocket solutions.

The relevant sections for Pusher, PieSocket and Ably can be found below:

- [Pusher - Publishing events](https://pusher.com/docs/channels/server_api/http-api/#publishing-events)
- [PieSocket - Publish with Python](https://www.piesocket.com/docs/3.0/python)
- [Ably - Sending a message](https://ably.com/documentation/quick-start-guide#sending-messages)

Wagtail Live provides a `PieSocketPublisher` which `publish` method is implemented as follows:

```python
# generic imports here

from wagtail_live.publishers.websocket import BaseWebsocketPublisher

from .utils import get_piesocket_api_key, get_piesocket_secret

logger = logging.getLogger(__name__)

publish_url = "https://www.piesocket.com/api/publish"
headers = {"Content-Type": "application/json"}

class PieSocketPublisher(BaseWebsocketPublisher):
    def publish(self, channel_id, renders, removals):
        payload = json.dumps(
            {
                "key": get_piesocket_api_key(),
                "secret": get_piesocket_secret(),
                "channelId": channel_id,
                "message": {"renders": renders, "removals": removals},
            }
        )

        # Publish update to PieSocket server
        response = requests.post(publish_url, headers=headers, data=payload)

        # Check for errors
        if not response.ok:
            logger.error("Failed publishing new update to PieSocket API.")
```

### Deploy a separate server

The design proposed here is heavily inspired from [this awesome guide](https://websockets.readthedocs.io/en/latest/howto/django.html) from the `websockets` library docs. Here is an extract explaining the idea:

> We need a event bus to enable communications between Django and websockets. Both sides connect permanently to the bus. Then Django writes events and websockets reads them. For the sake of simplicity, we’ll rely on Redis Pub/Sub.

Wagtail Live provides a `RedisPubSubPublisher` which implements the `publish` method.

If we want to use Redis Pub/Sub as en event bus, we can subclass the previous class as follows:

```python
from wagtail_live.publishers.redis import RedisPubSubPublisher

class MyWebsocketPublisher(RedisPubSubPublisher):
    pass
```

You can also provide your own event bus and implement the `publish` method accordingly.

In this architecture, we need to perform additional work to handle websocket connections.

#### Handle websocket connections

Let's create an `app.py` file inside the publisher module where we define the `app`.

At a lower level, the `app` is an async callable or an ASGI app that handles websocket connections in these steps:

1. Accept a websocket connection and add it to the event bus.
2. Send message to a websocket connection when a live page update is available.
2. Wait for a websocket connection to be closed and remove it from the event bus.

If our publisher inherits from `RedisPubSubPublisher`, we need to take these additional steps:

1. Define the `broadcast` coroutine and instantiate a `RedisBus`.
    
    The purpose of this coroutine is to send a message to a group of websocket connections:
    ```python
    import asyncio

    async def broadcast(message, recipients):
        """Broadcasts `message` to `recipients`."""

        await asyncio.wait([ws.send_method(message) for ws in recipients])
    ```
    In a real implementation, the `send_method` corresponds to the 'send' method of a websocket connection object in the library/framework used.

    For example, with `websockets` the `send_method` is `send` and with `starlette` it's `send_json`, `send_text` or `send_bytes`.

    With the `broadcast` method defined, we can now instantiate an event bus:
    ```python
    from wagtail_live.publishers.redis import RedisBus
    from wagtail_live.publishers.utils import get_redis_url

    bus = RedisBus(url=get_redis_url(), broadcast=broadcast)
    ```

2. Run the bus on startup.

    Finally, we'll need to 'run' the bus when the `app` starts running.

    This will depend on how the framework/library used handles running tasks on startup.

    For example, with `websockets` we can use the `serve` context manager and run the bus as long the the server is running:
    ```python
    import websockets

    async with websockets.serve(handler, host, port):
        await bus.run()  # Run the event bus forever
    ```

    > Starlette applications can register multiple event handlers for dealing with code that needs to run before the application starts up, or when the application is shutting down.

    ```python
    from starlette.applications import Starlette

    app = Starlette()

    @app.on_event("startup")
    def startup():
        # Run the event bus on startup
        asyncio.create_task(bus.run())
    ```

You can see [`StarlettePublisherApp`](https://github.com/wagtail/wagtail-live/blob/main/src/wagtail_live/publishers/starlette/app.py), [`WebsocketsPublisherApp`](https://github.com/wagtail/wagtail-live/blob/main/src/wagtail_live/publishers/websockets/app.py) and [`DjangoChannelsApp](https://github.com/wagtail/wagtail-live/blob/main/src/wagtail_live/publishers/django_channels/app.py) for complete implementations of the `app`.

#### Setup Django before running the `app`

Since we're using Django in a [standalone script](https://docs.djangoproject.com/en/3.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage), we need to call `django.setup()` before running the `app`:

```python
if __name__ == '__main__':
    import django
    django.setup()

    # Run the app here
```

## Client side logic

### Add javascript

### Add template

