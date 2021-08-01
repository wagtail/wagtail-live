import asyncio

import aioredis
import pytest

from wagtail_live.publishers.utils import get_redis_url


@pytest.fixture
async def redis():
    client = aioredis.from_url(get_redis_url(), decode_responses=True)
    yield client
    await client.connection_pool.disconnect()


async def wait_for_message(pubsub, timeout=0.1):
    # Copied from aioredis pubsub tests.
    now = asyncio.get_event_loop().time()
    timeout = now + timeout

    while now < timeout:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message is not None:
            return message

        await asyncio.sleep(0.01)
        now = asyncio.get_event_loop().time()

    return None
