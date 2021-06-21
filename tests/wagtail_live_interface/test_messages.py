""" Wagtail Live Interface Message test suite """

from unittest.mock import patch

from django.test import TestCase
from rest_framework import serializers

from wagtail_live_interface.models import DummyChannel, Message


class MessageAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""

        cls.channel = DummyChannel.objects.create(
            channel_name="Test channel",
        )
        cls.channel_name = cls.channel.channel_name

        cls.messages_count = 5
        for i in range(1, cls.messages_count + 1):
            Message.objects.create(
                channel=cls.channel,
                content=f"Message {i}",
            )

    def setUp(self):
        """Mock receiver to avoid sending new updates."""

        self.patcher = patch("wagtail_live_debug.receiver.WagtailLiveInterfaceReceiver")
        self.receiver_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def create_message(self, content="Some content"):
        """Helper to create a new message in self.channel.
        A default value is provided for the message content.
        """

        response = self.client.post(
            "/wagtail_live_interface/api/messages/",
            {
                "channel": self.channel_name,
                "content": content,
            },
        )
        return response

    def edit_message(self, message_id, new_content="Some content"):
        """Helper to edit a message in self.channel.
        A default value is provided for the new content of the message.
        """

        response = self.client.put(
            f"/wagtail_live_interface/api/messages/{message_id}/",
            {
                "channel": self.channel_name,
                "content": new_content,
            },
            content_type="application/json",
        )
        return response

    def delete_message(self, message_id):
        """Helper to delete a message."""

        response = self.client.delete(
            f"/wagtail_live_interface/api/messages/{message_id}/",
        )
        return response

    def test_retrieve_messages_from_api_status_code(self):
        """Response is 200 OK."""

        response = self.client.get("/wagtail_live_interface/api/messages/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_messages_from_api_count(self):
        """Response contains messages_count messages."""

        response = self.client.get("/wagtail_live_interface/api/messages/")
        self.assertEqual(len(response.json()), self.messages_count)

    def test_queryset_order_is_reversed(self):
        """Queryset order is reversed."""

        last_msg = Message.objects.get(id=5)
        self.assertEqual(Message.objects.first(), last_msg)

    def test_retrieve_message_from_api_status_code(self):
        """Response is 200 OK."""

        response = self.client.get("/wagtail_live_interface/api/messages/3/")
        self.assertEqual(response.status_code, 200)

    def test_retrieve_message_from_api(self):
        """Response contains expected message."""

        response = self.client.get("/wagtail_live_interface/api/messages/5/")

        exp_message = Message.objects.get(id=5)
        exp = {
            "id": exp_message.id,
            "channel": exp_message.channel.channel_name,
            "created": serializers.DateTimeField().to_representation(
                exp_message.created,
            ),
            "modified": exp_message.modified,
            "show": exp_message.show,
            "content": exp_message.content,
        }
        self.assertEqual(exp, response.json())

    def test_retrieve_non_existent_message_from_api(self):
        """Response is 404 Not Found."""

        response = self.client.get("/wagtail_live_interface/api/messages/23/")
        self.assertEqual(response.status_code, 404)

    def test_create_message_status_code(self):
        """Response is 201 CREATED."""

        response = self.create_message()
        self.assertEqual(response.status_code, 201)

    def test_create_message_returns_new_message_infos(self):
        """Response contains new message infos."""

        payload = self.create_message(content="A message content").json()

        self.assertEqual(payload["id"], 6)
        self.assertEqual(payload["channel"], self.channel_name)
        self.assertEqual(payload["content"], "A message content")

    def test_messages_count_after_message_creation(self):
        """Messages count has increased by 1."""

        self.create_message()
        self.assertEqual(Message.objects.count(), self.messages_count + 1)

    def test_query_created_message(self):
        """Newly created message is stored."""

        payload = self.create_message().json()
        new_message = Message.objects.get(id=payload["id"])

        self.assertEqual(new_message.channel, self.channel)
        self.assertEqual(new_message.content, "Some content")

    def test_create_message_with_non_existent_channel_fails(self):
        """Message isn't created. 400 Bad Request"""

        response = self.client.post(
            "/wagtail_live_interface/api/messages/",
            {
                "channel": "non-existent-channel",
                "content": "some content",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Message.objects.count(), self.messages_count)

    def test_edit_message_status_code(self):
        """Response is 200 OK."""

        response = self.edit_message(message_id=1)
        self.assertEqual(response.status_code, 200)

    def test_messages_count_after_message_edition(self):
        """Messages count hasn't changed."""

        self.edit_message(message_id=5)
        self.assertEqual(Message.objects.count(), self.messages_count)

    def test_edit_message_returns_edited_message_infos(self):
        """Response contains new message infos."""

        payload = self.edit_message(
            message_id=2,
            new_content="Edited content",
        ).json()

        self.assertEqual(payload["id"], 2)
        self.assertEqual(payload["channel"], self.channel_name)
        self.assertEqual(payload["content"], "Edited content")

    def test_query_edited_message(self):
        """Edited message is stored with new content."""

        self.assertEqual(Message.objects.get(id=4).content, "Message 4")

        self.edit_message(
            message_id=4,
            new_content="Edited content",
        )

        self.assertEqual(Message.objects.get(id=4).content, "Edited content")

    def test_edit_non_existent_message(self):
        """Response is 404 Not Found."""

        response = self.edit_message(message_id=6)
        self.assertEqual(response.status_code, 404)

    def test_edit_message_bad_channel(self):
        """Response is 400 Bad Request."""

        response = self.client.put(
            "/wagtail_live_debug/api/messages/3/",
            {
                "channel": "wrong_channel",
                "content": "Some content",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_message_status_code(self):
        """Response is 204 DELETED."""

        response = self.delete_message(message_id=1)
        self.assertEqual(response.status_code, 204)

    def test_messages_count_after_message_delete(self):
        """Channels count has decreased by 1."""

        self.delete_message(message_id=2)
        self.assertEqual(Message.objects.count(), self.messages_count - 1)

    def test_query_deleted_channel(self):
        """Deleted message does no longer exist."""

        id_message_to_delete = 3
        msg = "Message matching query does not exist"
        with self.assertRaisesMessage(Message.DoesNotExist, msg):
            self.delete_message(message_id=id_message_to_delete)
            Message.objects.get(id=id_message_to_delete)

    def test_delete_non_existent_message(self):
        """Response is 404 Not Found."""

        response = self.delete_message(message_id=6)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Message.objects.count(), self.messages_count)
