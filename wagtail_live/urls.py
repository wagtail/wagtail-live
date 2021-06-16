"""Wagtail Live URLs."""

from django.urls import path

from .publishers import IntervalPollingPublisherView

urlpatterns = [
    path("get-updates/<str:channel_id>/", IntervalPollingPublisherView.as_view()),
]
