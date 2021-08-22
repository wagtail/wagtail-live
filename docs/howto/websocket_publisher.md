# How to write a WebSocket publisher

This guide shows how to write a publisher following the WebSocket protocol.

There are three ways to add a WebSocket publisher to Wagtail Live:

1. Using [Django channels](https://channels.readthedocs.io/en/stable/), which is the classical way to add WebSocket support to a Django project.
    
    Wagtail Live already ships with a `DjangoChannelsPublisher`.

2. Use a hosted WebSocket solution.
    
    Examples: [Pusher](https://pusher.com/), [PieSocket](https://www.piesocket.com/), [Ably](https://ably.com/).

3. Deploy a separate server based on a framework or library that supports WebSocket.

    Examples: [Starlette](https://github.com/encode/starlette), [Websockets](https://github.com/aaugustin/websockets), [Tornado](https://www.tornadoweb.org/en/stable/).

In this guide, we will see how to add a WebSocket publisher using either a hosted third-party solution or by deploying a separate server. Here are the steps to follow for both methods:

1. Server-side logic: Inherit from [`BaseWebsocketPublisher`](https://wagtail.github.io/wagtail-live/reference/publishers/base_websocket_publisher/) and implement the `publish` method. This method handles publishing updates to websocket clients.

2. Client-side logic: Display updates when we receive them.


## Implement `publish` method

### Hosted WebSocket solutions

We have to check the third-party service's documentation to implement the `publish` method for hosted WebSocket solutions.

We can find the relevant sections for Pusher, PieSocket, and Ably below:

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

### Deploying a separate server

The design proposed here is heavily inspired by [this awesome guide](https://websockets.readthedocs.io/en/latest/howto/django.html) from the `websockets` library docs. Here is an extract explaining the idea:

> We need a event bus to enable communications between Django and websockets. Both sides connect permanently to the bus. Then Django writes events and websockets reads them. For the sake of simplicity, we’ll rely on Redis Pub/Sub.

Wagtail Live provides a `RedisPubSubPublisher` if we want to use Redis Pub/Sub as an event bus:

```python
from wagtail_live.publishers.redis import RedisPubSubPublisher

class MyWebsocketPublisher(RedisPubSubPublisher):
    pass
```

You can also provide your event bus and implement the `publish` method accordingly.

In this architecture, we need to perform additional work to handle WebSocket connections.

#### Handle WebSocket connections

Let's create an `app.py` file inside the publisher module where we define the `app`.

At a lower level, the `app` is an async callable or an ASGI app that handles WebSocket connections in these steps:

1. Accept a WebSocket connection and add it to the event bus.
2. Send a message to a WebSocket connection when a live page update is available.
2. Wait for a WebSocket connection to be closed and remove it from the event bus.

If our publisher inherits from `RedisPubSubPublisher`, we need to perform these steps:

1. Define the `broadcast` coroutine and instantiate a `RedisBus`.
    
    The purpose of the `broadcast` coroutine is to send a message to a group of WebSocket connections:

    ```python
    import asyncio

    async def broadcast(message, recipients):
        """Broadcasts `message` to `recipients`."""

        await asyncio.wait([ws.send_method(message) for ws in recipients])
    ```

    In a real implementation, the `send_method` corresponds to the 'send' method of a WebSocket connection object in the library/framework used.

    For example, with websockets the `send_method` is `send` and with starlette it's `send_json`, `send_text` or `send_bytes`.

    With the `broadcast` method defined, we can now instantiate an event bus:

    ```python
    from wagtail_live.publishers.redis import RedisBus
    from wagtail_live.publishers.utils import get_redis_url

    bus = RedisBus(url=get_redis_url(), broadcast=broadcast)
    ```

2. Run the bus on startup.

    Finally, we'll need to 'run' the bus when the `app` starts running.

    It will depend on how the framework/library used handles running tasks on startup.

    For example, with `websockets` we can use the `serve` context manager and run the bus as long as the server is running:

    ```python
    import websockets

    async with websockets.serve(handler, host, port):
        await bus.run()  # Run the event bus forever
    ```

    > Starlette applications can register multiple event handlers for dealing with code that needs to run before the application starts up, or when the application is shutting down:

    ```python
    from starlette.applications import Starlette

    app = Starlette()

    @app.on_event("startup")
    def startup():
        # Run the event bus on startup
        asyncio.create_task(bus.run())
    ```

You can see [`StarlettePublisherApp`](https://github.com/wagtail/wagtail-live/blob/main/src/wagtail_live/publishers/starlette/app.py), [`WebsocketsPublisherApp`](https://github.com/wagtail/wagtail-live/blob/main/src/wagtail_live/publishers/websockets/app.py) and [`DjangoChannelsApp`](https://github.com/wagtail/wagtail-live/blob/main/src/wagtail_live/publishers/django_channels/app.py) for complete implementations of the `app`.

#### Setup Django before running the `app`

Since we're using Django in a [standalone script](https://docs.djangoproject.com/en/3.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage), we need to call `django.setup()` before running the `app`:

```python
if __name__ == '__main__':
    import django
    django.setup()

    # Run the app here
```

## Client side logic

Let's add client side logic to display updates when we receive them from the server side.

### Add javascript

We need to open a WebSocket connection with the hosted WebSocket solution or the server-side for each client.

Wagtail Live provides a base `WebsocketPublisher` that takes a `baseURL` parameter.

It exposes the following interface:

- `initialize_websocket_connection`: Opens a WebSocket connection with the `baseURL` provided.
- `initialize_on_message_event`: Registers a callback on new message events.
- `initialize_on_error_event`: Registers a callback on disconnect/error events.
- `start` (Implemented): Registers WebSocket events callbacks after a WebSocket connection is opened.

### Hosted WebSocket solution

We need to check the docs of the third-party solution to find how to open a new connection with their services.

We can find the relevant sections for Pusher, PieSocket, and Ably below:

- [Pusher - Getting started](https://pusher.com/docs/channels/getting_started/javascript/)
- [PieSocket - Javascript client](https://www.piesocket.com/docs/3.0/javascript-client)
- [Ably - Receiving messages](https://ably.com/documentation/quick-start-guide#receiving-messages)

Here is a basic implementation of the Pusher client side logic:

```javascript
class PusherPublisher extends WebsocketPublisher {
    initialize_websocket_connection() {
        // Assuming that APP_KEY and APP_CLUSTER are defined in the Pusher template.
        var pusher = new Pusher(APP_KEY, {
            cluster: APP_CLUSTER,
        });

        // Assuming that the server side sends updates to the `channelID` channel.
        this.channel = pusher.subscribe(channelID);
    }

    initialize_on_message_event() {
        // Assuming that the server side sends updates with a live-page-update "event-name".
        this.channel.bind("live-page-update", (data) => {
            process_updates(data): // Wagtail Live utility
        });
    }
}

const publisher = new PusherPublisher(baseURL="");
publisher.start(); 
```

### Deploying a separate server

Wagtail Live provides a `GenericWebsocketPublisher` if we use the native `Websocket` library.

We can define our publisher like this if we use it:

```javascript
const baseURL = `${serverHost}:${serverPort}`;
const FrameworkOrLibraryPublisher = new GenericWebsocketPublisher(baseURL);
FrameworkOrLibraryPublisher.start(); 
```

### Add template

Finally, let's add the publisher template that will be included in the live page template.

This template links to the publisher's javascript code and defines the constants the latter uses.

#### Pusher example

The corresponding template for our `PusherPublisher` is:

```html
{% load publisher_tags static %}

<script src="https://js.pusher.com/7.0.3/pusher.min.js"></script>

<script>
    const API_KEY = "{% pusher_api_key %}"
    const API_CLUSTER = "{% pusher_api_cluster %}"
</script>

<script src="{% static 'wagtail_live/js/websocket/websocket.js' %}"></script>
<script src="{% static 'path/to/pusher.js' %}"></script>
```

Let's define the 'publisher tags'. 

In our project's `templatetags` module, we create a new file `publisher_tags.py` with the following:

```python
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def pusher_api_key():
    return settings.PUSHER_API_KEY


@register.simple_tag
def pusher_api_cluster():
    return settings.PUSHER_API_CLUSTER
```

#### Separate server example

```html
{% load static wagtail_live_tags %}

<script>
    const serverHost = "{% get_server_host %}";
    const serverPort = "{% get_server_port %}";
</script>

<script src="{% static 'wagtail_live/js/websocket/websocket.js' %}"></script>
<script src="{% static 'path/to/publisher.js' %}"></script> 
```

## Wrap up

We have a fully implemented WebSocket publisher.

To use it:

1. Add it in the live page model template.

    ```html
    {% include "wagtail_live/live_posts.html" %}
    {% include "path/to/publisher.html" %}
    ```

2. Specify `WAGTAIL_LIVE_PUBLISHER`.

    ```python
    WAGTAIL_LIVE_PUBLISHER = "path.to.my.websocket.publisher.MyWebsocketPublisher"
    ```

3. Specify additional settings

    In the `PusherPublisher` example, we'll have to define a `PUSHER_API_KEY` and a `PUSHER_API_CLUSTER` for example.

    For publishers based on a framework or library, we may need to specify `WAGTAIL_LIVE_SERVER_HOST` and `WAGTAIL_LIVE_SERVER_PORT`.