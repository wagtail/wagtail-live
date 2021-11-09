from django import template
from django.utils.dateparse import parse_datetime

register = template.Library()


@register.filter
def to_datetime(value):
    if not value:
        return ""
    if isinstance(value, str):
        value = parse_datetime(value)
    return value
