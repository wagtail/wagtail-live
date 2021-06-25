"""Wagtail Live URLs."""

from .utils import get_publisher

urlpatterns = []

publisher = get_publisher()
urlpatterns += publisher.get_urls()
