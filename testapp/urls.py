from django.conf import settings
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]


if settings.DEBUG:
    # Wagtail Live debug view
    from wagtail_live import urls as wagtail_live_urls  # noqa

    urlpatterns = [path("", include(wagtail_live_urls))] + urlpatterns

    # Static and media
    from django.conf.urls.static import static  # noqa
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    path("", include(wagtail_urls)),
]
