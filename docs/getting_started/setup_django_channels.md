# Set up Django Channels publisher

This document describes how to set up a publisher using the websocket technique and Django channels.

## Set up channels
### Install channels
First, follow the steps described [here](https://channels.readthedocs.io/en/stable/installation.html) to install `channels`.

### Add Wagtail Live websocket route
In your project's `asgi.py`, add Wagtail Live websocket route like this:
```python
# mysite/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from wagtail_live.publishers.django_channels import live_websocket_route

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wagtail_live_demo.settings.dev")

application = ProtocolTypeRouter({
"http": get_asgi_application(),
"websocket": AuthMiddlewareStack(
        URLRouter(
            live_websocket_route,
        )
    ),
})
```

### Enable a channel layer
The last step is to enable a channel layer. Follow the steps [here](https://channels.readthedocs.io/en/stable/tutorial/part_2.html#enable-a-channel-layer) to add a channel layer to your project.


## Configure `WAGTAIL_LIVE_PUBLISHER`

In order to use Django channels for the publishing part, add this to your `settings`:
```python
WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.django_channels.DjangoChannelsPublisher"
```

## Add publisher template

We also need to add this to our `live_blog_page.html` template:
```python
{% include "wagtail_live/websocket/django_channels.html" %}
```
