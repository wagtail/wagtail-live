import time

import pytest
from django.urls.resolvers import URLPattern

from wagtail_live.adapters.slack.receiver import (
    SlackEventsAPIReceiver,
    SlackWebhookMixin,
)
from wagtail_live.exceptions import RequestVerificationError
from wagtail_live.receivers import BaseMessageReceiver


@pytest.fixture
def slack_receiver():
    return SlackEventsAPIReceiver()


def test_slack_receiver_instance(slack_receiver):
    assert isinstance(slack_receiver, BaseMessageReceiver)
    assert isinstance(slack_receiver, SlackWebhookMixin)


# SlackWebhookMixin methods


def test_set_webhook(slack_receiver):
    assert slack_receiver.set_webhook() is None


def test_webhook_connection_set(slack_receiver):
    assert slack_receiver.webhook_connection_set()


def test_get_urls():
    patterns = SlackEventsAPIReceiver.get_urls()
    assert len(patterns) == 1

    pattern = patterns[0]
    assert isinstance(pattern, URLPattern)
    assert pattern.pattern._route == "slack/events"
    assert pattern.callback.view_class == SlackEventsAPIReceiver
    assert pattern.name == "slack_events_handler"


def test_verify_request_raises_error_if_no_timestampp(slack_receiver, rf):
    request = rf.post("/wagtail_live/slack/events")

    expected_err = "X-Slack-Request-Timestamp not found in request's headers."
    with pytest.raises(RequestVerificationError, match=expected_err):
        slack_receiver.verify_request(request, body="")


def test_verify_request_raises_timestamp_error(slack_receiver, rf):
    headers = {"HTTP_X-Slack-Request-Timestamp": f"{time.time() - 60 * 6}"}
    request = rf.post("/wagtail_live/slack/events", **headers)

    expected_err = "The request timestamp is more than five minutes from local time."
    with pytest.raises(RequestVerificationError, match=expected_err):
        slack_receiver.verify_request(request, body="")


def test_verify_request_raises_signature_error(slack_receiver, rf, settings):
    settings.SLACK_SIGNING_SECRET = "some-secret-not-so-secret"
    headers = {
        "HTTP_X-Slack-Request-Timestamp": f"{time.time()}",
        "HTTP_X-Slack-Signature": "random",
    }
    request = rf.post("/wagtail_live/slack/events", **headers)

    expected_err = "Slack signature couldn't be verified."
    with pytest.raises(RequestVerificationError, match=expected_err):
        slack_receiver.verify_request(request, body="")


def test_verify_request(slack_receiver, rf, settings):
    settings.SLACK_SIGNING_SECRET = "some-secret-not-so-secret"
    timestamp = f"{time.time()}"
    body = "body"
    headers = {
        "HTTP_X-Slack-Request-Timestamp": timestamp,
        "HTTP_X-Slack-Signature": "v0="
        + slack_receiver.sign_slack_request(content="v0:" + timestamp + ":" + body),
    }
    request = rf.post("/wagtail_live/slack/events", **headers)

    assert slack_receiver.verify_request(request, body=body) is None


@pytest.mark.django_db
def test_post_url_verification(slack_receiver, client, settings):
    settings.WAGTAIL_LIVE_RECEIVER = (
        "wagtail_live.adapters.slack.receiver.SlackEventsAPIReceiver"
    )
    data = {
        "type": "url_verification",
        "challenge": "challenge_token",
    }
    response = client.post(
        "/wagtail_live/slack/events", content_type="application/json", data=data
    )

    assert response.status_code == 200
    assert "challenge_token" in response.content.decode()


@pytest.mark.django_db
def test_post_request_verification_error(slack_receiver, client, settings):
    settings.WAGTAIL_LIVE_RECEIVER = (
        "wagtail_live.adapters.slack.receiver.SlackEventsAPIReceiver"
    )
    data = {"type": "some-type"}
    response = client.post(
        "/wagtail_live/slack/events", content_type="application/json", data=data
    )

    assert response.status_code == 403
    assert "Request verification failed." in response.content.decode()


@pytest.mark.django_db
def test_post(client, mocker, settings):
    settings.WAGTAIL_LIVE_RECEIVER = (
        "wagtail_live.adapters.slack.receiver.SlackEventsAPIReceiver"
    )
    data = {
        "token": "some-token",
        "type": "event_callback",
        "event": {
            "type": "message",
            "text": "This a test post.",
            "user": "user1",
            "ts": "1623319199.002300",
        },
    }
    mocker.patch.object(SlackEventsAPIReceiver, "verify_request")
    mocker.patch.object(SlackEventsAPIReceiver, "dispatch_event")
    response = client.post(
        "/wagtail_live/slack/events", content_type="application/json", data=data
    )

    SlackEventsAPIReceiver.dispatch_event.assert_called_once_with(event=data)
    assert response.status_code == 200
    assert "OK" in response.content.decode()
