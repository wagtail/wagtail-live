"""Wagtail Live test suite URLs"""

from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

from wagtail_live import urls as live_urls
from wagtail_live_interface import urls as live_interface_urls

urlpatterns = [
    path("wagtail_live_interface/", include(live_interface_urls)),
    path("wagtail_live/", include(live_urls)),
    path("admin/", include(wagtailadmin_urls)),
    path("", include(wagtail_urls)),
]
