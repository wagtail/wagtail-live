"""Wagtail Live test suite URLs"""

from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

from wagtail_live import urls as live_urls
from wagtail_live.webapp import urls as webapp_urls

urlpatterns = [
    path("wagtail_live/", include(live_urls)),
    path("webapp/", include(webapp_urls)),
    path("admin/", include(wagtailadmin_urls)),
    path("", include(wagtail_urls)),
]
