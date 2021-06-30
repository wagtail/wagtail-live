import hmac
import json
import time
from hashlib import sha256

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.http import HttpResponse

from wagtail_live.exceptions import RequestVerificationError
from wagtail_live.receivers import BaseMessageReceiver, WebhookReceiverMixin
from wagtail_live.utils import is_embed


class SlackWebhookMixin(WebhookReceiverMixin):
    """Slack WebhookMixin."""

    url_path = "slack/events"
    url_name = "slack_events_handler"

    def post(self, request, *args, **kwargs):
        """Checks if Slack is trying to verify our Request URL.

        Returns:
            (HttpResponse) containing the challenge string if Slack
            is trying to verify our request URL.
        """

        payload = json.loads(request.body.decode("utf-8"))
        if payload["type"] == "url_verification":
            return HttpResponse(payload["challenge"])
        return super().post(request, *args, **kwargs)

    @staticmethod
    def sign_slack_request(content):
        """Signs content from a Slack request using the SLACK_SIGNING_SECRET as key."""

        hasher = hmac.new(str.encode(settings.SLACK_SIGNING_SECRET), digestmod=sha256)
        hasher.update(str.encode(content))
        return hasher.hexdigest()

    def verify_request(self, request, body):
        """Verifies Slack requests.
        See https://api.slack.com/authentication/verifying-requests-from-slack.

        Args:
            request (HttpRequest): from Slack

        Raises:
            (RequestVerificationError) if request failed to be verified.
        """

        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        if not timestamp:
            raise RequestVerificationError(
                "X-Slack-Request-Timestamp not found in request's headers."
            )

        if abs(time.time() - float(timestamp)) > 60 * 5:
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            raise RequestVerificationError(
                "The request timestamp is more than five minutes from local time."
            )

        sig_basestring = "v0:" + timestamp + ":" + body
        my_signature = "v0=" + self.sign_slack_request(content=sig_basestring)
        slack_signature = request.headers["X-Slack-Signature"]
        if not hmac.compare_digest(slack_signature, my_signature):
            raise RequestVerificationError("Slack signature couldn't be verified.")

    @classmethod
    def set_webhook(cls):
        """This is done in Slack UI."""

        pass

    @classmethod
    def webhook_connection_set(cls):
        """Assume that it's true."""

        return True


class SlackEventsAPIReceiver(BaseMessageReceiver, SlackWebhookMixin):
    """Slack Events API receiver."""

    def dispatch_event(self, event):
        """See base class."""

        message = event["event"]
        if "subtype" in message and message["subtype"] == "message_changed":
            self.change_message(message=message)
            return

        elif "subtype" in message and message["subtype"] == "message_deleted":
            self.delete_message(message=message)
            return

        else:
            self.add_message(message=message)

    def get_channel_id_from_message(self, message):
        """See base class."""

        return message["channel"]

    def get_message_id_from_message(self, message):
        """See base class."""

        return message["ts"]

    def get_message_text(self, message):
        """See base class."""

        return message["text"]

    def get_message_files(self, message):
        """See base class."""

        return message["files"] if "files" in message else []

    def get_image_title(self, image):
        """See base class."""

        return image["title"]

    def get_image_name(self, image):
        """See base class."""

        return image["name"]

    def get_image_mimetype(self, image):
        """See base class."""

        return image["mimetype"].split("/")[1]

    def get_image_dimensions(self, image):
        """See base class."""

        try:
            return (image["original_w"], image["original_h"])
        except KeyError:
            raise ValueError

    def get_image_content(self, image):
        """See base class."""

        slack_bot_token = getattr(settings, "SLACK_BOT_TOKEN", "")
        if not slack_bot_token:
            raise ImproperlyConfigured(
                "You haven't specified SLACK_BOT_TOKEN in your settings."
                + "You won't be able to upload images from Slack without this setting defined."
            )
        headers = {"Authorization": f"Bearer {slack_bot_token}"}
        response = requests.get(image["url_private"], headers=headers)
        return ContentFile(response.content)

    def get_message_id_from_edited_message(self, message):
        """See base class."""

        return self.get_message_id_from_message(message=message["previous_message"])

    def get_message_text_from_edited_message(self, message):
        """See base class."""

        return self.get_message_text(message=message["message"])

    def get_message_files_from_edited_message(self, message):
        """See base class."""

        return self.get_message_files(message=message["message"])

    def get_embed(self, text):
        """Strips leading `<` and trailing `>` from Slack urls."""

        return text[1:-1] if is_embed(text=text[1:-1]) else ""
