import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from wagtail_live.publishers.piesocket import (
    get_piesocket_api_key,
    get_piesocket_endpoint,
    get_piesocket_secret,
)


def test_get_piesocket_api_key_setting_missing():
    get_piesocket_api_key.cache_clear()
    expected_err = "You haven't specified a PieSocket API Key in your settings."

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_piesocket_api_key()


@override_settings(PIESOCKET_API_KEY="api-key")
def test_get_piesocket_api_key():
    get_piesocket_api_key.cache_clear()

    assert get_piesocket_api_key() == "api-key"


def test_get_piesocket_secret_setting_missing():
    get_piesocket_secret.cache_clear()
    expected_err = "You haven't specified a PieSocket secret in your settings."

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_piesocket_secret()


@override_settings(PIESOCKET_SECRET="secret")
def test_get_piesocket_secret():
    get_piesocket_secret.cache_clear()

    assert get_piesocket_secret() == "secret"


def test_get_piesocket_endpoint_setting_missing():
    get_piesocket_endpoint.cache_clear()
    expected_err = "You haven't specified a PieSocket endpoint in your settings."

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        get_piesocket_endpoint()


@override_settings(PIESOCKET_ENDPOINT="endpoint")
def test_get_piesocket_endpoint():
    get_piesocket_endpoint.cache_clear()

    assert get_piesocket_endpoint() == "endpoint"
