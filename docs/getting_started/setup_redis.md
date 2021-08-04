# Set up redis based event bus

<<<<<<< HEAD
<<<<<<< HEAD
This document describes how to set up an event bus with Redis, for Wagtail Live publishers.
=======
This document describes how to setup an event bus with redis for Wagtail Live publishers.
>>>>>>> Add docs for redis and starlette
=======
This document describes how to set up an event bus with Redis, for Wagtail Live publishers.
>>>>>>> Apply suggestions from code review

An event bus provides an abstraction over the [Publish/Subscribe pattern](https://en.wikipedia.org/wiki/Publish-subscribe_pattern).

The goal of the event bus in Wagtail Live is the following:

<<<<<<< HEAD
<<<<<<< HEAD
- **Publisher**: A live page sends a new message containing its recent modifications to its channel group. Each live page is associated to a unique channel group.
=======
- **Publisher**: A live page sends a new message containing its recent modifications to its channel group. Each live page is associated to an unique channel group.
>>>>>>> Add docs for redis and starlette
=======
- **Publisher**: A live page sends a new message containing its recent modifications to its channel group. Each live page is associated to a unique channel group.
>>>>>>> Apply suggestions from code review

- **Subscriber**: The users viewing a page in live subscribe to that page's channel group and receive the page modifications as soon as possible.

Redis provides [PubSub commands](https://redis.io/topics/pubsub).
We will then need to install `redis` and `aioredis`. The latter provides asyncio Redis support.

## Install redis

<<<<<<< HEAD
<<<<<<< HEAD
Follow the steps outlined [here](https://redis.io/topics/quickstart) to install Redis.

Whenever you want to test your application, you will have to start the Redis server.
=======
Follow the steps outlined [here](https://redis.io/topics/quickstart) to install redis.

Whenever you want to test your application, you will have to spin the redis server.
>>>>>>> Add docs for redis and starlette
=======
Follow the steps outlined [here](https://redis.io/topics/quickstart) to install Redis.

Whenever you want to test your application, you will have to start the Redis server.
>>>>>>> Apply suggestions from code review

If you have `docker` installed, you can run this command:
```console
docker run -p 6379:6379 -d redis:5
```

## Install aioredis

To install [aioredis](https://github.com/aio-libs/aioredis-py), type:
```console
$ pip install aioredis
<<<<<<< HEAD
<<<<<<< HEAD
```
=======
```
>>>>>>> Add docs for redis and starlette
=======
```
>>>>>>> Apply suggestions from code review
