# How to write a WebSocket publisher based on a hosted WebSocket solution

This guide shows how to write a Wagtail Live publisher based on a hosted WebSocket solution. Examples: [Pusher](https://pusher.com/), [PieSocket](https://www.piesocket.com/), [Ably](https://ably.com/).

In this guide, we will provide examples for Pusher.

Wagtail Live supports PieSocket; you can see its implementation for another example.

Here are the steps we need to take, regardless of the solution used:

1. Server-side logic: Inherit from [`BaseWebsocketPublisher`](https://wagtail.github.io/wagtail-live/reference/publishers/base_websocket_publisher/) and implement the `publish` method. 

    This method handles publishing updates to websocket clients.

2. Client-side logic: Display updates when we receive them.

## Server-side logic: implement `publish` method

We have to check the third-party service's documentation to implement the `publish` method.

We can find the relevant sections for Pusher, PieSocket, and Ably below:

- [Pusher - Publishing events](https://pusher.com/docs/channels/server_api/http-api/#publishing-events)
- [PieSocket - Publish with Python](https://www.piesocket.com/docs/3.0/python)
- [Ably - Sending a message](https://ably.com/documentation/quick-start-guide#sending-messages)

Following the Pusher docs, here is how we can implement it:

```python
import pusher
from django.conf import settings

from wagtail_live.publishers.websocket import BaseWebsocketPublisher


class PusherPublisher(BaseWebsocketPublisher):
    client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID, 
        key=settings.PUSHER_APP_KEY, 
        secret=settings.PUSHER_APP_SECRET, 
        cluster=settings.PUSHER_APP_CLUSTER,
    )

    def publish(self, channel_id, renders, removals):
        self.client.trigger(
            channel_id,
            "live-page-update",
            {'renders': renders, 'removals': removals},
        )
```

## Client side logic

Let's add client side logic to display updates when we receive them from the third-party services server.

### Add javascript

We need to open a WebSocket connection with the hosted WebSocket solution for each client.

Wagtail Live provides a base `WebsocketPublisher` that takes a `baseURL` parameter.

It exposes the following interface:

- `initialize_websocket_connection`: Opens a WebSocket connection with the `baseURL` provided.
- `initialize_on_message_event`: Registers a callback on new message events.
- `initialize_on_error_event`: Registers a callback on disconnect/error events.
- `start` (Implemented): Registers WebSocket events callbacks after a WebSocket connection is opened.

We need to check the docs of the third-party solution to find how to open a new connection with their services.

We can find the relevant sections for Pusher, PieSocket, and Ably below:

- [Pusher - Getting started](https://pusher.com/docs/channels/getting_started/javascript/)
- [PieSocket - Javascript client](https://www.piesocket.com/docs/3.0/javascript-client)
- [Ably - Receiving messages](https://ably.com/documentation/quick-start-guide#receiving-messages)

Here is a basic implementation of the Pusher client side's logic:

```javascript
class PusherPublisher extends WebsocketPublisher {
    initialize_websocket_connection() {
        var pusher = new Pusher(APP_KEY, {
            cluster: APP_CLUSTER,
        });
        this.channel = pusher.subscribe(channelID);
    }

    initialize_on_message_event() {
        this.channel.bind("live-page-update", (data) => {
            process_updates(data): // Wagtail Live utility
        });
    }
}

const publisher = new PusherPublisher(baseURL="");
publisher.start(); 
```

### Add template

Finally, let's add the publisher template that will be included in the live page template.

This template links to the publisher's javascript code and defines the constants the latter uses.

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
    return settings.PUSHER_APP_KEY


@register.simple_tag
def pusher_api_cluster():
    return settings.PUSHER_APP_CLUSTER
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

    In the `PusherPublisher` example, we'll have to define `PUSHER_APP_KEY`, `PUSHER_APP_CLUSTER`, `PUSHER_APP_ID`, and `PUSHER_APP_SECRET` in our settings for example.
