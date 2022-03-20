import time
from datetime import datetime

import pytest
import requests
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.test import override_settings
from django.urls import resolve
from django.urls.resolvers import URLPattern
from wagtail.images.models import Image

from tests.testapp.models import BlogPage
from tests.utils import get_test_image_file, reload_urlconf
from wagtail_live import blocks
from wagtail_live.exceptions import RequestVerificationError
from wagtail_live.receivers.base import IMAGE, TEXT, BaseMessageReceiver
from wagtail_live.receivers.slack import SlackEventsAPIReceiver, SlackWebhookMixin


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
    expected_err = "X-Slack-Request-Timestamp not found in request's headers."
    with pytest.raises(RequestVerificationError, match=expected_err):
        slack_receiver.verify_request(request=rf.post("/"), body="")


def test_verify_request_raises_timestamp_error(slack_receiver, rf):
    headers = {"HTTP_X-Slack-Request-Timestamp": f"{time.time() - 60 * 6}"}
    expected_err = "The request timestamp is more than five minutes from local time."

    with pytest.raises(RequestVerificationError, match=expected_err):
        slack_receiver.verify_request(request=rf.post("/", **headers), body="")


@override_settings(SLACK_SIGNING_SECRET="some-secret-not-so-secret")
def test_verify_request_raises_signature_error(slack_receiver, rf):
    headers = {
        "HTTP_X-Slack-Request-Timestamp": f"{time.time()}",
        "HTTP_X-Slack-Signature": "random",
    }
    expected_err = "Slack signature couldn't be verified."

    with pytest.raises(RequestVerificationError, match=expected_err):
        slack_receiver.verify_request(request=rf.post("/", **headers), body="")


@override_settings(SLACK_SIGNING_SECRET="some-secret-not-so-secret")
def test_verify_request(slack_receiver, rf, settings):
    timestamp = f"{time.time()}"
    body = "body"
    headers = {
        "HTTP_X-Slack-Request-Timestamp": timestamp,
        "HTTP_X-Slack-Signature": "v0="
        + slack_receiver.sign_slack_request(content="v0:" + timestamp + ":" + body),
    }
    request = rf.post("/", **headers)

    assert slack_receiver.verify_request(request, body=body) is None


@pytest.fixture(scope="class")
@override_settings(
    WAGTAIL_LIVE_RECEIVER="wagtail_live.receivers.slack.SlackEventsAPIReceiver"
)
def reload_urls():
    reload_urlconf()
    resolved = resolve("/wagtail_live/slack/events")

    assert resolved.url_name == "slack_events_handler"


@pytest.mark.usefixtures("reload_urls")
class TestPostSlackEventsAPIReceiver:
    def test_post_url_verification(self, slack_receiver, client):
        data = {
            "type": "url_verification",
            "challenge": "challenge_token",
        }
        response = client.post(
            "/wagtail_live/slack/events", content_type="application/json", data=data
        )

        assert response.status_code == 200
        if not hasattr(response, "headers"):  # Django < 2.2
            assert response._headers["content-type"][1] == "plain/text"
        else:
            assert response.headers["content-type"] == "plain/text"
        assert "challenge_token" in response.content.decode()

    def test_post_request_verification_error(self, slack_receiver, client):
        data = {"type": "event_callback"}
        response = client.post(
            "/wagtail_live/slack/events", content_type="application/json", data=data
        )

        assert response.status_code == 403
        assert "Request verification failed." in response.content.decode()

    def test_post(self, client, mocker):
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


# BaseMessageReceiver methods


def test_dispatch_new_message(slack_receiver, slack_message, mocker):
    mocker.patch.object(slack_receiver, "add_message")
    slack_receiver.dispatch_event(event=slack_message)

    message = slack_message["event"]
    slack_receiver.add_message.assert_called_once_with(message=message)


def test_dispatch_edited_message(slack_receiver, slack_edited_message, mocker):
    mocker.patch.object(slack_receiver, "change_message")
    slack_receiver.dispatch_event(event=slack_edited_message)

    message = slack_edited_message["event"]
    slack_receiver.change_message.assert_called_once_with(message=message)


def test_dispatch_deleted_message(slack_receiver, slack_deleted_message, mocker):
    mocker.patch.object(slack_receiver, "delete_message")
    slack_receiver.dispatch_event(event=slack_deleted_message)

    message = slack_deleted_message["event"]
    slack_receiver.delete_message.assert_called_once_with(message=message)


def test_dispatch_image_message(slack_receiver, slack_image_message, mocker):
    mocker.patch.object(slack_receiver, "add_message")
    slack_receiver.dispatch_event(event=slack_image_message)

    message = slack_image_message["event"]
    slack_receiver.add_message.assert_called_once_with(message=message)


def test_dispatch_other_subtype_message(
    slack_receiver, slack_channel_join_message, mocker
):
    mocker.patch.object(slack_receiver, "add_message")
    mocker.patch.object(slack_receiver, "change_message")
    mocker.patch.object(slack_receiver, "delete_message")

    slack_receiver.dispatch_event(event=slack_channel_join_message)

    slack_receiver.add_message.assert_not_called()
    slack_receiver.change_message.assert_not_called()
    slack_receiver.delete_message.assert_not_called()


def test_get_channel_id_from_message(slack_receiver, slack_message):
    message = slack_message["event"]
    channel_id = slack_receiver.get_channel_id_from_message(message=message)

    assert channel_id == message["channel"]


def test_get_message_id_from_message(slack_receiver, slack_message):
    message = slack_message["event"]
    message_id = slack_receiver.get_message_id_from_message(message=message)

    assert message_id == message["ts"]


def test_get_message_text(slack_receiver, slack_message):
    message = slack_message["event"]
    message_text = slack_receiver.get_message_text(message=message)

    assert message_text == message["text"]


def test_get_message_files_if_no_files(slack_receiver, slack_message):
    message = slack_message["event"]
    message_files = slack_receiver.get_message_files(message=message)

    assert message_files == []


def test_get_message_files_if_files(slack_receiver, slack_image_message):
    message = slack_image_message["event"]
    message_files = slack_receiver.get_message_files(message=message)

    assert message_files == message["files"]


def test_get_image_title(slack_receiver, slack_image_message):
    message = slack_image_message["event"]
    image = slack_receiver.get_message_files(message=message)[0]
    image_title = slack_receiver.get_image_title(image=image)

    assert image_title == image["title"]


def test_get_image_name(slack_receiver, slack_image_message):
    message = slack_image_message["event"]
    image = slack_receiver.get_message_files(message=message)[0]
    image_name = slack_receiver.get_image_name(image=image)

    assert image_name == image["name"]


def test_get_image_mimetype(slack_receiver, slack_image_message):
    message = slack_image_message["event"]
    image = slack_receiver.get_message_files(message=message)[0]
    image_mimetype = slack_receiver.get_image_mimetype(image=image)

    assert image_mimetype == "png"


def test_get_image_dimensions(slack_receiver, slack_image_message):
    message = slack_image_message["event"]
    image = slack_receiver.get_message_files(message=message)[0]
    image_dimensions = slack_receiver.get_image_dimensions(image=image)

    assert image_dimensions == (image["original_w"], image["original_h"])


def test_get_image_dimensions_raises_value_error(slack_receiver):
    with pytest.raises(ValueError):
        slack_receiver.get_image_dimensions(image={})


def test_get_image_content_missing_token(slack_receiver):
    expected_err = (
        "You haven't specified SLACK_BOT_TOKEN in your settings."
        + "You won't be able to upload images from Slack without this setting defined."
    )

    with pytest.raises(ImproperlyConfigured, match=expected_err):
        slack_receiver.get_image_content(image={})


@override_settings(SLACK_BOT_TOKEN="some-token")
def test_get_image_content(slack_receiver, mocker):
    class ResponseMock:
        content = b""

    mocker.patch.object(requests, "get", return_value=ResponseMock())
    image_content = slack_receiver.get_image_content(image={"url_private": "some-url"})

    assert isinstance(image_content, ContentFile)
    assert image_content.read() == b""


def test_get_message_id_from_edited_message(slack_receiver, slack_edited_message):
    message = slack_edited_message["event"]
    message_id = slack_receiver.get_message_id_from_edited_message(message=message)

    assert message_id == message["message"]["ts"]


def test_get_message_text_from_edited_message(slack_receiver, slack_edited_message):
    message = slack_edited_message["event"]
    message_text = slack_receiver.get_message_text_from_edited_message(message=message)

    assert message_text == message["message"]["text"]


def test_get_files_from_edited_message(slack_receiver, slack_edited_image_message):
    message = slack_edited_image_message["event"]
    message_files = slack_receiver.get_message_files_from_edited_message(
        message=message
    )

    assert message_files == message["message"]["files"]


def test_get_files_from_edited_message_if_no_files(
    slack_receiver, slack_edited_message
):
    message = slack_edited_message["event"]
    message_files = slack_receiver.get_message_files_from_edited_message(
        message=message
    )

    assert message_files == []


def test_get_embed_if_embed(slack_receiver):
    slack_embed_url = (
        "<https://www.youtube.com/watch?v=Cq3LOsf2kSY"
        "|"
        "https://www.youtube.com/watch?v=Cq3LOsf2kSY>"
    )
    got = slack_receiver.get_embed(text=slack_embed_url)

    assert got == slack_embed_url[1:-1].split("|")[0]


def test_get_embed_if_not_embed_1(slack_receiver):
    assert slack_receiver.get_embed("Not embed") == ""


def test_get_embed_if_not_embed_2(slack_receiver):
    slack_url = "<https://www.youtube.com/|https://www.youtube.com/>"
    got = slack_receiver.get_embed(text=slack_url)

    assert got == ""


def test_parse_text_valid_url_format_1(slack_receiver):
    text = "This message contains a URL <http://example.com/>."
    got = slack_receiver.parse_text(text=text)

    assert got == (
        "This message contains a URL <a href='http://example.com/'>http://example.com/</a>."
    )


def test_parse_text_valid_url_format_2(slack_receiver):
    text = "So does this one: <http://example.com|www.example.com>"
    got = slack_receiver.parse_text(text=text)

    assert got == "So does this one: <a href='http://example.com'>www.example.com</a>"


def test_parse_text_invalid_url_format_1(slack_receiver):
    text = "<Some text>"
    got = slack_receiver.parse_text(text=text)

    assert got == text


def test_parse_text_invalid_url_format_2(slack_receiver):
    text = "<http:Some text|More text>"
    got = slack_receiver.parse_text(text=text)

    assert got == text


def test_parse_text_invalid_url_format_3(slack_receiver):
    text = "<http:Some text|More text|More more text>"
    got = slack_receiver.parse_text(text=text)

    assert got == text


@pytest.fixture
def slack_page(blog_page_factory):
    """Creates a live page corresponding to slack_channel in Slack."""

    return blog_page_factory(channel_id="slack_channel")


@pytest.mark.django_db
def test_add_message(slack_receiver, slack_message, slack_page):
    assert len(BlogPage.objects.first().live_posts) == 0

    message = slack_message["event"]
    slack_receiver.add_message(message=message)

    live_page = BlogPage.objects.first()
    assert len(live_page.live_posts) == 1

    live_post_added = live_page.live_posts[-1].value
    assert live_post_added["message_id"] == message["ts"]

    message_parts = message["text"].split("\n")
    content = live_post_added["content"]
    assert len(content) == len(message_parts)

    assert content[0].block_type == TEXT
    assert content[0].value.source == message_parts[0]

    assert content[-1].block_type == TEXT
    assert content[-1].value.source == message_parts[-1]


@pytest.mark.django_db
def test_add_message_inexistent_channel(
    slack_receiver, slack_message, mocker, slack_page
):
    # Set wrong channel
    message = slack_message["event"]
    message["channel"] = "not_slack_channel"

    mocker.patch.object(blocks, "construct_live_post_block")
    slack_receiver.add_message(message=message)

    blocks.construct_live_post_block.assert_not_called()


@pytest.mark.django_db
def test_change_message(
    slack_receiver, slack_embed_message, slack_edited_message, slack_page
):

    # Add the message to edit
    message = slack_embed_message["event"]
    slack_receiver.add_message(message=message)

    message_added = BlogPage.objects.first().live_posts[-1]
    previous_id = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value.source == "This is another test post."

    # Edit the message
    edited_message = slack_edited_message["event"]
    slack_receiver.change_message(message=edited_message)

    message_added = BlogPage.objects.first().live_posts[-1]
    id_after_edit = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value.source == "This is another test post that has been edited."

    # ID is preserved.
    assert previous_id == id_after_edit


@pytest.mark.django_db
def test_change_message_wrong_channel(
    slack_receiver, slack_embed_message, slack_edited_message, slack_page
):
    message = slack_embed_message["event"]
    slack_receiver.add_message(message=message)

    message_added = BlogPage.objects.first().live_posts[-1]
    previous_id = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value.source == "This is another test post."

    edited_message = slack_edited_message["event"]
    edited_message["channel"] = "not_slack_channel"
    slack_receiver.change_message(message=edited_message)

    message_added = BlogPage.objects.first().live_posts[-1]
    id_after_edit = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value.source == "This is another test post."

    assert previous_id == id_after_edit


@pytest.mark.django_db
def test_delete_message(
    slack_receiver, slack_embed_message, slack_deleted_message, slack_page
):
    message = slack_embed_message["event"]
    slack_receiver.add_message(message=message)
    assert len(BlogPage.objects.first().live_posts) == 1

    deleted_message = slack_deleted_message["event"]
    slack_receiver.delete_message(message=deleted_message)
    assert len(BlogPage.objects.first().live_posts) == 0


@pytest.mark.django_db
def test_delete_message_wrong_channel(
    slack_receiver, slack_embed_message, slack_deleted_message, slack_page
):
    message = slack_embed_message["event"]
    slack_receiver.add_message(message=message)
    assert len(BlogPage.objects.first().live_posts) == 1

    deleted_message = slack_deleted_message["event"]
    deleted_message["channel"] = "not_slack_channel"
    slack_receiver.delete_message(message=deleted_message)
    assert len(BlogPage.objects.first().live_posts) == 1


@pytest.mark.django_db
def test_process_files(slack_receiver, slack_image_message, mocker):
    message = slack_image_message["event"]
    files = slack_receiver.get_message_files(message=message)
    image = files[0]

    image_content = get_test_image_file(
        filename=slack_receiver.get_image_name(image=image),
        size=slack_receiver.get_image_dimensions(image=image),
    )
    mocker.patch.object(slack_receiver, "get_image_content", return_value=image_content)
    live_post = blocks.construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    slack_receiver.process_files(live_post=live_post, files=files)

    post_content = live_post["content"]
    assert post_content[0].block_type == IMAGE

    post_value = post_content[0].value
    assert isinstance(post_value, Image)
    assert post_value.title == image["title"]
    assert (post_value.width, post_value.height) == slack_receiver.get_image_dimensions(
        image=image
    )


def test_process_files_bad_dimensions(slack_receiver, slack_image_message, caplog):
    live_post = blocks.construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    files = [{"title": "test.png"}]

    assert slack_receiver.process_files(live_post=live_post, files=files) is None
    assert caplog.messages[0] == "Unable to retrieve the dimensions of test.png"


def test_process_files_bad_mimetype(slack_receiver, slack_image_message, caplog):
    live_post = blocks.construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    message = slack_image_message["event"]
    files = slack_receiver.get_message_files(message=message)
    image = files[0]
    image["mimetype"] = "image/bad_mimetype"
    assert slack_receiver.process_files(live_post=live_post, files=files) is None
    assert (
        caplog.messages[0]
        == "Couldn't upload test_image.png. Images of type bad_mimetype aren't supported yet."
    )
