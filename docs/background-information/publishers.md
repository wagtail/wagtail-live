# What publisher is right for you?

Wagtail Live supports various publishers. 
Their task is to update the live page every time a post is created.

## Interval polling 

Interval polling is Javascript running in the browser, that asks the webserver for updates with a regular interval.
Wagtail Live has a configurable interval, the default is 3 seconds. This value is typically between seconds and a couple of minutes.

Even if there are no new posts, the request is made.
This is server-resource heavy and doesn't scale well.

➕

- Easy to set up
- Normal HTTP protocol

➖

- Can take up to the interval time for a post to appear
- Server resource-heavy
- Does not scale

_Use interval polling on low-traffic websites, and when update delay isn't an issue._

[Set up interval polling](/getting_started/publishers/setup_interval_polling/)

## Long polling

Long polling is a bit like interval polling. The difference is that the server keeps the connection open for the interval time.
This way, there is always an open connection. Updates can be sent the moment they are created. Updates appear instantaneous.

➕

- Easy to set up
- Instant updates
- Normal HTTP protocol

➖

- Server resource-heavy
- Does not scale
- Server can only handle a finite amount of connections

_Use long polling for low-volume sites, evaluation, and demonstration purposes._

[Set up long polling](/getting_started/publishers/setup_long_polling/)

## WebSocket

A [WebSocket](https://datatracker.ietf.org/doc/html/rfc6455) is the better choice. Wagtail Live supports multiple ways to set up a WebSocket.

Traditionally, Python applications (like Django/Wagtail) use the Web Server Gateway Interface ([WSGI](https://wsgi.readthedocs.io/en/latest/index.html)) to communicate between application and server.
HTTP and WSGI are designed to handle a request response cycle. A browser requests an URL, the webserver serves the response. One at the time.
This kind of setup is event based. It only does something when a request comes in, and idles for the rest of the time. 

The WebSocket protocol is more advanced, lightweight and server resource friendly. 
It allows a persistent connection between server and browser. It is set up once and used for a long time.
Communication is full-duplex. Messages can be sent from server to browser, and the other way around.
This kind of setup runs an event loop and handles messages as they occur. 
Note that we talk about messages and not request/response. A message doesn't have a response.
Maybe a message triggers the application to send another message. But, in the meantime, other messages can be sent and received. It is asynchronous.

To use the WebSocket protocol, the server and applications need support asynchronous communications.

➕

- Lightweight on server resources
- Persistent connection
- Instant updates
- Handles many users

➖

- Takes more effort to set up

!!! note
    Websockets are full-duplex. However, Wagtail Live only sends messages to the browser.

### Piesocket

[Piesocket](https://www.piesocket.com/) is software-as-a-service.
Run your Django/Wagtail application like normal. Use Piesocket to handle the WebSocket.

Create an account, set up the credentials, and you are ready to go.

[Set up Piesocket](/getting_started/publishers/setup_piesocket/)

### Django Channels

With [Django Channels](https://channels.readthedocs.io/), you'll have a single application handling both HTTP and WS protocols.

Django Channels runs your application over [ASGI](https://asgi.readthedocs.io) and requires [Daphne](https://github.com/django/daphne).
Daphne is a pure-Python ASGI server, maintained by members of the Django project.

[Set up Django Channels](/getting_started/publishers/setup_django_channels/)

### Starlette

[Starlette](https://www.starlette.io) is a lightweight toolkit for building high-performance WebSocket service.
You need to run a [ASGI](https://asgi.readthedocs.io) server, such as [Uvicorn](https://www.uvicorn.org), [Daphne](https://github.com/django/daphne), or [Hypercorn](https://pgjones.gitlab.io/hypercorn/).

Start both the ASGI server for the Websocket and your Django/Wagtail application.

[Set up Starlette](/getting_started/publishers/setup_starlette/)

### Websockets

[Websockets](https://websockets.readthedocs.io) is a library for building WebSocket server. It is built on top of Asyncio, Python’s standard asynchronous I/O framework.

Start both the Websockets server for the Websocket and your Django/Wagtail application.

[Set up Websockets](/getting_started/publishers/setup_websockets/)
