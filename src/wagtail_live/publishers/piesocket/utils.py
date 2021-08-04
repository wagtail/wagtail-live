from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@lru_cache(maxsize=1)
def get_piesocket_api_key():
    """Retrieves user's piesocket API key.

    Returns:
        (str) Piesocket API key.

    Raises:
        (ImproperlyConfigured) if the piesocket API key isn't specified in settings.
    """

    api_key = getattr(settings, "PIESOCKET_API_KEY", None)
    if not api_key:
        raise ImproperlyConfigured(
            "Specify PIESOCKET_API_KEY if you intend to use Piesocket as publisher."
        )
    return api_key


@lru_cache(maxsize=1)
def get_piesocket_secret():
    """Retrieves user's piesocket secret.

    Returns:
        (str) Piesocket secret.

    Raises:
        (ImproperlyConfigured) if the piesocket secret isn't specified in settings.
    """

    secret = getattr(settings, "PIESOCKET_SECRET", None)
    if not secret:
        raise ImproperlyConfigured(
            "Specify PIESOCKET_SECRET if you intend to use Piesocket as publisher."
        )
    return secret


@lru_cache(maxsize=1)
def get_piesocket_endpoint():
    """Retrieves user's piesocket endpoint.

    Returns:
        (str) Piesocket endpoint.

    Raises:
        (ImproperlyConfigured) if the piesocket endpoint isn't specified in settings.
    """

    endpoint = getattr(settings, "PIESOCKET_ENDPOINT", None)
    if not endpoint:
        raise ImproperlyConfigured(
            "Specify PIESOCKET_ENDPOINT if you intend to use Piesocket as publisher."
        )
    return endpoint
