from django.template import Context, Template
from django.test import override_settings

from wagtail_live.publishers.piesocket.utils import (
    get_piesocket_api_key,
    get_piesocket_endpoint,
)

context = Context({})


def test_get_server_host_tag():
    to_render = Template("{% load wagtail_live_tags %}" "{% get_server_host %}")
    rendered = to_render.render(context)

    assert rendered == "localhost"  # Default value


def test_get_server_port_tag():
    to_render = Template("{% load wagtail_live_tags %}" "{% get_server_port %}")
    rendered = to_render.render(context)

    assert rendered == "8765"  # Default value


@override_settings(PIESOCKET_API_KEY="some-key")
def test_piesocket_api_key_tag():
    get_piesocket_api_key.cache_clear()
    to_render = Template("{% load wagtail_live_tags %}" "{% piesocket_api_key %}")
    rendered = to_render.render(context)

    assert rendered == "some-key"  # Default value


@override_settings(PIESOCKET_ENDPOINT="some-endpoint")
def test_piesocket_endpoint_tag():
    get_piesocket_endpoint.cache_clear()
    to_render = Template("{% load wagtail_live_tags %}" "{% piesocket_endpoint %}")
    rendered = to_render.render(context)

    assert rendered == "some-endpoint"  # Default value
