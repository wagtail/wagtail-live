from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def get_redis_url():
    return getattr(settings, "WAGTAIL_LIVE_REDIS_URL", "redis://127.0.0.1:6379/1")


@lru_cache(maxsize=1)
def get_live_server_host():
    return getattr(settings, "WAGTAIL_LIVE_SERVER_HOST", "localhost")


@lru_cache(maxsize=1)
def get_live_server_port():
    return getattr(settings, "WAGTAIL_LIVE_SERVER_PORT", 8765)
