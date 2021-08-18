from django import template

from wagtail_live.publishers.piesocket import (
    get_piesocket_api_key,
    get_piesocket_endpoint,
)
from wagtail_live.publishers.utils import get_live_server_host, get_live_server_port

register = template.Library()


@register.simple_tag
def piesocket_api_key():
    return get_piesocket_api_key()


@register.simple_tag
def piesocket_endpoint():
    return get_piesocket_endpoint()


@register.simple_tag
def get_server_host():
    return get_live_server_host()


@register.simple_tag
def get_server_port():
    return get_live_server_port()
