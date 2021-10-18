from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase


class AuthenticationTests(TestCase):
    def test_missing_webapp_login_url_setting(self):
        expected = (
            "You haven't specified the WEBAPP_LOGIN_URL in your settings. "
            "It is required if you intend to use the webapp interface."
        )
        with self.assertRaisesMessage(ImproperlyConfigured, expected):
            self.client.get("/webapp/channels/")

    def test_login_required_for_channels_views(self):
        webapp_login_url = "/login/"

        with self.settings(WEBAPP_LOGIN_URL=webapp_login_url):
            response = self.client.get("/webapp/channels/")
            self.assertEqual(response.url, f"{webapp_login_url}?next=/webapp/channels/")

            response = self.client.get("/webapp/channels/channel_2/")
            self.assertEqual(
                response.url, f"{webapp_login_url}?next=/webapp/channels/channel_2/"
            )

    def test_auth_required_for_api_views(self):
        webapp_login_url = "/login/"

        with self.settings(WEBAPP_LOGIN_URL=webapp_login_url):
            response = self.client.post(
                "/webapp/api/channels/",
                {"channel_name": "test"},
            )
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                response.json(),
                {"detail": "Authentication credentials were not provided."},
            )
