from django import template

from wagtail_live.publishers.piesocket import (
    get_piesocket_api_key,
    get_piesocket_endpoint,
)

register = template.Library()


@register.simple_tag
def piesocket_api_key():
    return get_piesocket_api_key()


@register.simple_tag
def piesocket_endpoint():
    return get_piesocket_endpoint()
