# Set up Websockets publisher

This document describes how to set up a publisher using the websocket technique and [Websockets](https://github.com/aaugustin/websockets). `Websockets` is an efficient library for building WebSocket servers and clients in Python.



## Set up event bus

First, follow the steps in [set up an event bus](setup_event_bus_redis.md). 

## Install websockets
Install `websockets`:

```console
$ pip install websockets
```

## Configure `WAGTAIL_LIVE_PUBLISHER`

In order to use `websockets` for the publishing part, add this to your `settings`:

```python
WAGTAIL_LIVE_PUBLISHER = "wagtail_live.publishers.websockets.WebsocketsPublisher"
```

## Configure server host and port

In this architecture, you will need a separate server to handle websocket connections.
You can define the server's host and port in your settings file by doing so:

```python
WAGTAIL_LIVE_SERVER_HOST = "my-server-host" # Defaults to `localhost`.
WAGTAIL_LIVE_SERVER_PORT = "my-server-port" # Defaults to `8765`.
```

In development mode, you can use the following command to start the server:
```console
python manage.py run_publisher websockets
```

## Add publisher template

We also need to add this to our `live_blog_page.html` template:
```python
{% include "wagtail_live/websocket/websockets.html" %}
```
