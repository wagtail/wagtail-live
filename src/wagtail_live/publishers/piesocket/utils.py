from functools import lru_cache

from wagtail_live.utils import get_setting_or_raise


@lru_cache(maxsize=1)
def get_piesocket_api_key():
    """
    Retrieves user's Piesocket API key.

    Returns:
        (str) Piesocket API key.

    Raises:
        (ImproperlyConfigured) if the Piesocket API key isn't specified in settings.
    """

    return get_setting_or_raise(
        setting="PIESOCKET_API_KEY", setting_str="PieSocket API Key"
    )


@lru_cache(maxsize=1)
def get_piesocket_secret():
    """
    Retrieves user's piesocket secret.

    Returns:
        (str) Piesocket secret.

    Raises:
        (ImproperlyConfigured) if the piesocket secret isn't specified in settings.
    """

    return get_setting_or_raise(
        setting="PIESOCKET_SECRET", setting_str="PieSocket secret"
    )


@lru_cache(maxsize=1)
def get_piesocket_endpoint():
    """
    Retrieves user's piesocket endpoint.

    Returns:
        (str) Piesocket endpoint.

    Raises:
        (ImproperlyConfigured) if the piesocket endpoint isn't specified in settings.
    """

    return get_setting_or_raise(
        setting="PIESOCKET_ENDPOINT", setting_str="PieSocket endpoint"
    )
