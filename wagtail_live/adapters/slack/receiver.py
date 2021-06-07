""" How to use it?
To create an app, register your URL to slack, get a token plus all additional infrastucture, see:
https://github.com/slackapi/bolt-python/tree/main/examples/django
Then do something like this in your url_patterns:
from wagtail_live.slack.views import slack_events_handler
url_patterns += [
    path("slack/events", slack_events_handler, name="slack_events_handler"),
]
Add the following to your settings.py file:
LIVE_PAGE_MODEL = "model name"
LIVE_APP = "app name"
SLACK_BOT_TOKEN = "your slack bot token"
SLACK_SIGNING_SECRET = "your slack signing secret"
And you are good to go! (Soon hopefully!)
"""

from wagtail_live.receivers import BaseMessageReceiver, is_embed


class SlackEventsAPIReceiver(BaseMessageReceiver):
    """Slack Events API receiver."""

    def dispatch(self, event):
        """See base class."""

        message = event
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
        """ Strips leading `<` and trailing `>` from Slack urls."""

        if is_embed(text=text[1:-1]):
            # Not sure if it's the normal behavior, but have repeatedly received links
            # from SLack API that looks like below:
            # <https://twitter.com/lephoceen/status/139?s=20|https://twitter.com/lephoceen/status/139?s=20>'
            return text[1:-1].split("|")[0]
        return ""