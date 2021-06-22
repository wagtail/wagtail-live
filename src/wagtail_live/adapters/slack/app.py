from django.conf import settings
from slack_bolt import App

from .receiver import SlackEventsAPIReceiver

app = App(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
    token_verification_enabled=False,
)

slack_receiver = SlackEventsAPIReceiver()


@app.event("message")
def handle_message_events(body, ack):
    slack_receiver.dispatch(body["event"])
    ack()
