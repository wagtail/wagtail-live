""" Webapp Image test suite """

from django.contrib.auth.models import User
from django.test import TestCase

from tests.utils import get_test_image_file
from wagtail_live.webapp.models import Channel, Image, Message


class ImageAPITests(TestCase):
    def setUp(self):
        channel = Channel.objects.create(channel_name="test_channel")
        message = Message.objects.create(channel=channel, content="Some content")

        image_content = get_test_image_file()
        self.image = Image.objects.create(message=message, image=image_content)
        self.user = User.objects.create(username="Tester")
        self.client.force_login(self.user)

    def tearDown(self):
        self.client.logout()
        self.image.image.delete()

    def test_delete_image(self):
        self.assertEqual(Image.objects.count(), 1)
        response = self.client.delete(f"/webapp/api/images/{self.image.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Image.objects.count(), 0)

    def test_delete_image_wrong_pk(self):
        self.assertEqual(Image.objects.count(), 1)
        response = self.client.delete("/webapp/api/images/2/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Image.objects.count(), 1)
