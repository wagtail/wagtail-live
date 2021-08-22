# How to write a WebSocket publisher

There are three ways to add a WebSocket publisher to Wagtail Live:

## Using [Django channels](https://channels.readthedocs.io/en/stable/)

It's the classical way to add WebSocket support to a Django project.
    
Wagtail Live already ships with a `DjangoChannelsPublisher`.

## Use a hosted WebSocket solution.
    
Examples: [Pusher](https://pusher.com/), [PieSocket](https://www.piesocket.com/), [Ably](https://ably.com/).

See: [How to write a WebSocket publisher based on a hosted WebSocket solution](hosted_websocket_solution.md).

## Deploy a separate server based on a framework or library that supports WebSocket.

Examples: [Starlette](https://github.com/encode/starlette), [Websockets](https://github.com/aaugustin/websockets), [Tornado](https://www.tornadoweb.org/en/stable/).

See: [How to write a WebSocket publisher based on a framework/library](framework_library.md).