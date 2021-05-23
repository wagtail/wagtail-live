""" Test suite for Wagtail Live models."""

from django.test import TestCase
from wagtail.core.models import Page


class TestSimpleLivePage(TestCase):
    fixtures = ["test.json"]

    def setUp(self):
        self.live_page = Page.objects.get(id=3).specific

    def test_get_channel_name(self):
        """ Ensure channel's name is properly set."""

        channel_name = self.live_page.channel_name
        self.assertEqual(channel_name, "SimpleLiveChannel")
