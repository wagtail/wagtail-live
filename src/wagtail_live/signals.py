"""Wagtail Live signals."""

import django.dispatch

live_page_update = django.dispatch.Signal()
