""" Webapp Message test suite """

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIClient

from tests.utils import get_test_image_file
from wagtail_live.webapp.models import Channel, Image, Message


class MessageAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""

        cls.user = User.objects.create(username="Tester")
        cls.channel = Channel.objects.create(
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
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Mock receiver to avoid sending new updates.
        self.patcher = patch("wagtail_live.webapp.views.LIVE_RECEIVER.dispatch_event")
        self.receiver_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def tearDown(self):
        self.client.force_authenticate(user=None)

    def create_message(self, content="Some content", images=[]):
        """
        Helper to create a new message in self.channel.
        A default value is provided for the message content.
        """

        response = self.client.post(
            "/webapp/api/messages/",
            {
                "channel": self.channel_name,
                "content": content,
                "images": [],
            },
        )
        return response

    def test_new_update_sent_on_message_created(self):
        response = self.create_message()
        self.receiver_mock.assert_called_once_with(
            event={
                "update_type": 1,
                "id": 6,
                "channel": "Test channel",
                "created": response.context["message"]["created"],
                "modified": None,
                "show": True,
                "content": "Some content",
                "images": [],
            }
        )

    def edit_message(self, message_id, new_content="Some content"):
        """
        Helper to edit a message in self.channel.
        A default value is provided for the new content of the message.
        """

        response = self.client.put(
            f"/webapp/api/messages/{message_id}/",
            {
                "channel": self.channel_name,
                "content": new_content,
            },
        )
        return response

    def test_new_update_sent_on_message_edited(self):
        response = self.edit_message(
            message_id=3,
            new_content="Edited content",
        )

        self.receiver_mock.assert_called_once_with(
            event={
                "update_type": 2,
                "id": 3,
                "channel": "Test channel",
                "created": response.context["message"]["created"],
                "modified": response.context["message"]["modified"],
                "show": True,
                "content": "Edited content",
                "images": [],
            }
        )

    def test_new_update_sent_with_side_effect(self):
        self.receiver_mock.side_effect = KeyError
        response = self.edit_message(
            message_id=3,
            new_content="Edited content",
        )
        # No error.
        self.assertEqual(response.status_code, 200)

    def delete_message(self, message_id):
        """Helper to delete a message."""

        response = self.client.delete(
            f"/webapp/api/messages/{message_id}/",
        )
        return response

    def test_new_update_sent_on_message_deleted(self):
        self.delete_message(message_id=2)
        self.receiver_mock.assert_called_once_with(
            event={
                "update_type": 3,
                "channel": "Test channel",
                "id": 2,
            }
        )

    def test_queryset_order_is_reversed(self):
        last_msg = Message.objects.get(id=5)
        self.assertEqual(Message.objects.first(), last_msg)

    def test_create_message_status_code(self):
        response = self.create_message()
        self.assertEqual(response.status_code, 201)

    def test_create_message_returns_new_message_infos(self):
        payload = self.create_message(content="A message content").context["message"]

        self.assertEqual(payload["id"], 6)
        self.assertEqual(payload["channel"], self.channel_name)
        self.assertEqual(payload["content"], "A message content")

    def test_messages_count_after_message_creation(self):
        self.create_message()
        self.assertEqual(Message.objects.count(), self.messages_count + 1)

    def test_query_created_message(self):
        payload = self.create_message().context["message"]
        new_message = Message.objects.get(id=payload["id"])

        self.assertEqual(new_message.channel, self.channel)
        self.assertEqual(new_message.content, "Some content")

    def test_create_message_with_non_existent_channel_fails(self):
        response = self.client.post(
            "/webapp/api/messages/",
            {
                "channel": "non-existent-channel",
                "content": "some content",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Message.objects.count(), self.messages_count)

    def test_create_message_with_image(self):
        self.assertEqual(Image.objects.count(), 0)
        response = self.client.post(
            "/webapp/api/messages/",
            {
                "channel": self.channel_name,
                "content": "Some content",
                "images": [get_test_image_file()],
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.count(), 1)

        image_model = Image.objects.first()
        image = image_model.image
        self.assertEqual(
            response.context["message"]["images"],
            [
                {
                    "id": image_model.id,
                    "image": {
                        "name": image.name,
                        "url": image.url,
                        "width": image.width,
                        "height": image.height,
                    },
                }
            ],
        )

        # Cleanup
        image.delete()

    def test_edit_message_status_code(self):
        response = self.edit_message(message_id=1)
        self.assertEqual(response.status_code, 200)

    def test_messages_count_after_message_edition(self):
        self.edit_message(message_id=5)
        self.assertEqual(Message.objects.count(), self.messages_count)

    def test_edit_message_returns_edited_message_infos(self):
        payload = self.edit_message(
            message_id=2,
            new_content="Edited content",
        ).context["message"]

        self.assertEqual(payload["id"], 2)
        self.assertEqual(payload["channel"], self.channel_name)
        self.assertEqual(payload["content"], "Edited content")

    def test_query_edited_message(self):
        self.assertEqual(Message.objects.get(id=4).content, "Message 4")

        self.edit_message(
            message_id=4,
            new_content="Edited content",
        )

        self.assertEqual(Message.objects.get(id=4).content, "Edited content")

    def test_edit_non_existent_message(self):
        response = self.edit_message(message_id=6)
        self.assertEqual(response.status_code, 404)

    def test_edit_message_bad_channel(self):
        response = self.client.put(
            "/webapp/api/messages/3/",
            {
                "channel": "wrong_channel",
                "content": "Some content",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_message_with_image(self):
        self.assertEqual(Message.objects.get(id=1).images.count(), 0)
        data = {
            "channel": self.channel_name,
            "content": "Edited content",
        }
        files = {"images": [get_test_image_file()]}

        with patch.object(Request, "_parse", return_value=(data, files)):
            response = self.client.put("/webapp/api/messages/1/", {})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Message.objects.get(id=1).images.count(), 1)

        # Cleanup
        Image.objects.first().image.delete()

    def test_delete_message_status_code(self):
        response = self.delete_message(message_id=1)
        self.assertEqual(response.status_code, 204)

    def test_messages_count_after_message_delete(self):
        self.delete_message(message_id=2)
        self.assertEqual(Message.objects.count(), self.messages_count - 1)

    def test_query_deleted_message(self):
        id_message_to_delete = 3
        msg = "Message matching query does not exist"
        with self.assertRaisesMessage(Message.DoesNotExist, msg):
            self.delete_message(message_id=id_message_to_delete)
            Message.objects.get(id=id_message_to_delete)

    def test_delete_non_existent_message(self):
        response = self.delete_message(message_id=6)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Message.objects.count(), self.messages_count)
