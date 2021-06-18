"""Slack receivers."""

import time
from hmac import compare_digest

from django.http import HttpResponse

from wagtail_live.exceptions import RequestVerificationError
from wagtail_live.receivers import BaseMessageReceiver, WebhookReceiverMixin
from wagtail_live.utils import is_embed, sign_slack_request


class SlackWebhookMixin(WebhookReceiverMixin):
    """Slack WebhookMixin."""

    url_path = "slack/events"
    url_name = "slack_events_handler"

    def pre_check_request(self, request, body, payload):
        """Checks if Slack is trying to verify our Request URL.

        Returns:
            (HttpResponse) containing the challenge string if Slack
            is trying to verify our request URL.
        """

        if payload["type"] == "url_verification":
            return HttpResponse(payload["challenge"])

    def verify_request(self, request, body, payload):
        """Verifies Slack requests.
        See https://api.slack.com/authentication/verifying-requests-from-slack.

        Args:
            request (HttpRequest): from Slack

        Raises:
            (RequestVerificationError) if request failed to be verified.
        """

        timestamp = request.headers["X-Slack-Request-Timestamp"]
        if abs(time.time() - float(timestamp)) > 60 * 5:
            # The request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it.
            raise RequestVerificationError

        sig_basestring = "v0:" + timestamp + ":" + body
        my_signature = "v0=" + sign_slack_request(sig_basestring)
        slack_signature = request.headers["X-Slack-Signature"]

        if not compare_digest(slack_signature, my_signature):
            raise RequestVerificationError

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

        if is_embed(text=text[1:-1]):
            # Not sure if it's the normal behavior, but have repeatedly received links
            # from SLack API that looks like below:
            # <https://twitter.com/lephoceen/status/139?s=20|https://twitter.com/lephoceen/status/139?s=20>'
            return text[1:-1].split("|")[0]
        return ""
