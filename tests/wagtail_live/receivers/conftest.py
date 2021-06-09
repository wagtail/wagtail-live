import pytest

from wagtail_live.adapters.slack.receiver import SlackEventsAPIReceiver


@pytest.fixture
def slack_receiver():
    """Fixture representing a Slack receiver instance."""

    return SlackEventsAPIReceiver(app_name="testapp", model_name="SimpleLivePage")
