""" Webapp Channel test suite """

from django.contrib.auth.models import User
from django.test import TestCase

from wagtail_live.webapp.models import Channel


class ChannelTestCaseSetUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""

        cls.channels_count = 5
        for i in range(1, cls.channels_count + 1):
            Channel.objects.create(
                channel_name=f"channel_{i}",
            )
        cls.user = User.objects.create(username="Tester")

    def setUp(self):
        self.client.force_login(self.user)


class ChannelViewsTests(ChannelTestCaseSetUp):
    def test_channels_listing_status_code(self):
        response = self.client.get("/webapp/channels/")
        self.assertEqual(response.status_code, 200)

    def test_channels_listing_count(self):
        response = self.client.get("/webapp/channels/")
        self.assertEqual(len(response.context["channels"]), self.channels_count)

    def test_channel_listing_status_code(self):
        response = self.client.get("/webapp/channels/channel_3/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_channel(self):
        response = self.client.get("/webapp/channels/channel_1/")
        channel_exp = Channel.objects.get(channel_name="channel_1")
        channel_got = response.context["channel"]

        self.assertEqual(channel_exp, channel_got)

    def test_retrieve_non_existent_channel(self):
        response = self.client.get("/webapp/channels/non_existent/")
        self.assertEqual(response.status_code, 404)


class ChannelAPITests(ChannelTestCaseSetUp):
    def create_channel(self, channel_name):
        """Helper to create a new channel."""

        response = self.client.post(
            "/webapp/api/channels/",
            {"channel_name": channel_name},
        )
        return response

    def delete_channel(self, channel_name):
        """Helper to delete a channel."""

        response = self.client.delete(
            f"/webapp/api/channels/{channel_name}/",
        )
        return response

    def test_queryset_order_is_reversed(self):
        first_channel = Channel.objects.get(channel_name="channel_1")
        self.assertEqual(Channel.objects.last(), first_channel)

    def test_create_channel_status_code(self):
        response = self.create_channel(channel_name="channel_6")
        self.assertEqual(response.status_code, 201)

    def test_create_channel_returns_new_channel_name(self):
        response = self.create_channel(channel_name="new_channel_name")
        self.assertEqual(response.json()["channel_name"], "new_channel_name")

    def test_channels_count_after_channel_creation(self):
        self.create_channel(channel_name="new_channel")
        self.assertEqual(Channel.objects.count(), self.channels_count + 1)

    def test_query_created_channel(self):
        self.create_channel(channel_name="new_channel")
        new_channel = Channel.objects.get(channel_name="new_channel")
        self.assertEqual(new_channel.channel_name, "new_channel")

    def test_create_channel_with_already_existing_channel(self):
        response = self.create_channel("channel_1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Channel.objects.count(), self.channels_count)

    def test_delete_channel_status_code(self):
        response = self.delete_channel(channel_name="channel_4")
        self.assertEqual(response.status_code, 204)

    def test_channels_count_after_channel_delete(self):
        self.delete_channel(channel_name="channel_2")
        self.assertEqual(Channel.objects.count(), self.channels_count - 1)

    def test_query_deleted_channel(self):
        channel_to_delete = "channel_1"
        msg = "Channel matching query does not exist"
        with self.assertRaisesMessage(Channel.DoesNotExist, msg):
            self.delete_channel(channel_name=channel_to_delete)
            Channel.objects.get(channel_name=channel_to_delete)

    def test_delete_non_existent_channel(self):
        response = self.delete_channel(channel_name="non_existent_channel")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Channel.objects.count(), self.channels_count)
