""" Wagtail Live test suite URLs """

from django.urls import include, path

from live_debug_view import urls as debug_view_urls

urlpatterns = [
    path("debug_view/", include(debug_view_urls)),
]
