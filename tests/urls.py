"""Wagtail Live test suite URLs"""

from django.conf import settings
from django.urls import include, path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

from wagtail_live.adapters.slack.views import slack_events_handler
from wagtail_live_debug import urls as live_debug_urls

urlpatterns = [
    path("wagtail_live_debug/", include(live_debug_urls)),
    path("slack/events", slack_events_handler, name="slack_events_handler"),
    path("admin/", include(wagtailadmin_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = urlpatterns + [
    path("", include(wagtail_urls)),
]
