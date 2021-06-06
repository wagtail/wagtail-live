"""Wagtail Live test suite URLs"""

from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

from wagtail_live_debug import urls as live_debug_urls

urlpatterns = [
    path("wagtail_live_debug/", include(live_debug_urls)),
    path("admin/", include(wagtailadmin_urls)),
    path("", include(wagtail_urls)),
]
