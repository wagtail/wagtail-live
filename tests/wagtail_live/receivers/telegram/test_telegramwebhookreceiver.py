from datetime import datetime

import pytest
import requests
from django.core.files.base import ContentFile
from django.test import override_settings
from django.urls import resolve, reverse

from tests.utils import get_test_image_file, reload_urlconf
from wagtail_live.blocks import construct_live_post_block
from wagtail_live.exceptions import WebhookSetupError
from wagtail_live.receivers.base import EMBED, IMAGE, BaseMessageReceiver
from wagtail_live.receivers.telegram import (
    TelegramWebhookMixin,
    TelegramWebhookReceiver,
    get_base_telegram_url,
)


@pytest.fixture
def telegram_receiver():
    return TelegramWebhookReceiver()


def test_telegram_receiver_instance(telegram_receiver):
    assert isinstance(telegram_receiver, BaseMessageReceiver)
    assert isinstance(telegram_receiver, TelegramWebhookMixin)


# TelegramWebhookMixin methods


class ResponseMock:
    def __init__(self, ok, json_data):
        self.ok = ok
        self.json_data = json_data

    def ok(self):
        return self.ok

    def json(self):
        return self.json_data


@pytest.fixture
@override_settings(
    WAGTAIL_LIVE_RECEIVER="wagtail_live.receivers.telegram.TelegramWebhookReceiver"
)
def reload_urls(mocker):
    mocker.patch.object(
        TelegramWebhookReceiver, "webhook_connection_set", return_value=True
    )
    reload_urlconf()
    resolved = resolve("/wagtail_live/telegram/events/telegram-token/")

    assert resolved.url_name == "telegram_events_handler"


@pytest.fixture
def telegram_overrides():
    with override_settings(
        TELEGRAM_BOT_TOKEN="telegram-token", TELEGRAM_WEBHOOK_URL="www.webhook.com"
    ):
        yield


@pytest.mark.usefixtures("telegram_overrides")
class TestTelegramwebhookMixin:
    def test_verify_request(self, client, mocker, reload_urls):
        mocker.patch.object(
            TelegramWebhookReceiver, "dispatch_event", return_value=None
        )
        response = client.post(
            reverse("telegram_events_handler", kwargs={"token": "telegram-token"}),
            content_type="application/json",
            data={},
        )
        assert response.status_code == 200

    def test_verify_request_bad_token(self, client, reload_urls):
        response = client.post(
            reverse(
                "telegram_events_handler", kwargs={"token": "wrong-telegram-token"}
            ),
            content_type="application/json",
            data={},
        )

        assert response.status_code == 403
        assert "Request verification failed." in response.content.decode()

    def test_webhook_connection_set(self, mocker):
        json_data = {
            "ok": True,
            "result": {
                "url": "www.webhook.com/wagtail_live/telegram/events/telegram-token/",
            },
        }
        mocker.patch.object(
            requests, "get", return_value=ResponseMock(ok=True, json_data=json_data)
        )

        assert TelegramWebhookReceiver.webhook_connection_set() is True

    def test_webhook_connection_set_response_not_ok(self, mocker):
        json_data = {
            "ok": True,
            "result": {
                "url": "www.webhook.com/wagtail_live/telegram/events/telegram-token/",
            },
        }
        mocker.patch.object(
            requests, "get", return_value=ResponseMock(ok=False, json_data=json_data)
        )

        assert TelegramWebhookReceiver.webhook_connection_set() is False

    def test_webhook_connection_set_result_not_ok(self, mocker):
        json_data = {
            "ok": False,
            "result": {
                "url": "www.webhook.com/wagtail_live/telegram/events/telegram-token/",
            },
        }
        mocker.patch.object(
            requests, "get", return_value=ResponseMock(ok=True, json_data=json_data)
        )

        assert TelegramWebhookReceiver.webhook_connection_set() is False

    def test_webhook_connection_set_different_webhook_got(self, mocker):
        json_data = {
            "ok": True,
            "result": {
                "url": "www.different-url.com",
            },
        }
        mocker.patch.object(
            requests, "get", return_value=ResponseMock(ok=True, json_data=json_data)
        )

        assert TelegramWebhookReceiver.webhook_connection_set() is False

    def test_set_webhook(self, mocker):
        json_data = {"ok": True}
        mocker.patch.object(
            requests, "get", return_value=ResponseMock(ok=True, json_data=json_data)
        )

        assert TelegramWebhookReceiver.set_webhook() is None

    def test_set_webhook_raises_error(self, mocker):
        json_data = {"ok": False, "result": True, "description": "Webhook wasn't set"}
        mocker.patch.object(
            requests, "get", return_value=ResponseMock(ok=True, json_data=json_data)
        )

        expected_err = (
            "Failed to set Webhook connection with Telegram's API. Webhook wasn't set"
        )
        with pytest.raises(WebhookSetupError, match=expected_err):
            TelegramWebhookReceiver.set_webhook()


# BaseMessageReceiver methods


def test_dispatch_new_message(telegram_receiver, telegram_message, mocker):
    mocker.patch.object(telegram_receiver, "add_message")
    telegram_receiver.dispatch_event(event=telegram_message)

    message = telegram_message["message"]
    telegram_receiver.add_message.assert_called_once_with(message=message)


def test_dispatch_new_channel_post(telegram_receiver, telegram_channel_post, mocker):
    mocker.patch.object(telegram_receiver, "add_message")
    telegram_receiver.dispatch_event(event=telegram_channel_post)

    message = telegram_channel_post["channel_post"]
    telegram_receiver.add_message.assert_called_once_with(message=message)


def test_dispatch_edited_message(telegram_receiver, telegram_edited_message, mocker):
    mocker.patch.object(telegram_receiver, "change_message")
    telegram_receiver.dispatch_event(event=telegram_edited_message)

    message = telegram_edited_message["edited_message"]
    telegram_receiver.change_message.assert_called_once_with(message=message)


def test_dispatch_edited_channel_post(
    telegram_receiver, telegram_edited_channel_post, mocker
):
    mocker.patch.object(telegram_receiver, "change_message")
    telegram_receiver.dispatch_event(event=telegram_edited_channel_post)

    message = telegram_edited_channel_post["edited_channel_post"]
    telegram_receiver.change_message.assert_called_once_with(message=message)


def test_dispatch_bot_command(telegram_receiver, telegram_bot_command, mocker):
    mocker.patch.object(telegram_receiver, "handle_bot_command")
    telegram_receiver.dispatch_event(event=telegram_bot_command)

    message = telegram_bot_command["message"]
    telegram_receiver.handle_bot_command.assert_called_once_with(message=message)


def test_handle_bot_command(telegram_receiver, telegram_bot_command, mocker):
    mocker.patch.object(
        requests, "get", return_value=ResponseMock(ok=True, json_data={"ok": True})
    )
    message = telegram_bot_command["message"]
    chat_id = telegram_receiver.get_channel_id_from_message(message)

    assert telegram_receiver.handle_bot_command(message=message) is None
    requests.get.assert_called_once_with(
        get_base_telegram_url() + "sendMessage",
        params={
            "chat_id": chat_id,
            "text": chat_id,
        },
    )


def test_handle_other_bot_commands(
    telegram_receiver, telegram_bot_other_command, mocker
):
    mocker.patch.object(requests, "get", return_value=None)
    message = telegram_bot_other_command["message"]

    assert telegram_receiver.handle_bot_command(message=message) is None
    requests.get.assert_not_called()


def test_handle_bot_command_error(
    telegram_receiver, telegram_bot_command, mocker, caplog
):
    json_data = {"ok": False, "description": "Failed sending message"}
    mocker.patch.object(
        requests, "get", return_value=ResponseMock(ok=True, json_data=json_data)
    )

    message = telegram_bot_command["message"]
    telegram_receiver.handle_bot_command(message=message)
    assert caplog.messages[0] == "Failed sending message"


def test_get_channel_id_from_message(telegram_receiver, telegram_message):
    message = telegram_message["message"]
    channel_id = telegram_receiver.get_channel_id_from_message(message=message)

    assert channel_id == str(message["chat"]["id"])


def test_get_message_id_from_message(telegram_receiver, telegram_message):
    message = telegram_message["message"]
    message_id = telegram_receiver.get_message_id_from_message(message=message)

    assert message_id == str(message["message_id"])


def test_get_message_id_from_media_message(telegram_receiver, telegram_media_message_1):
    message = telegram_media_message_1["message"]
    message_id = telegram_receiver.get_message_id_from_message(message=message)

    assert message_id == str(message["media_group_id"])


def test_get_message_text(telegram_receiver, telegram_message):
    message = telegram_message["message"]
    message_text = telegram_receiver.get_message_text(message=message)

    assert message_text == {"text": message["text"], "entities": []}


def test_get_message_text_image_message(telegram_receiver, telegram_image_message):
    message = telegram_image_message["message"]
    message_text = telegram_receiver.get_message_text(message=message)

    assert message_text == {"text": message["caption"], "entities": []}


def test_get_telegram_message_text_with_entities(
    telegram_receiver, telegram_message_with_entities
):
    message = telegram_message_with_entities["message"]
    message_text = telegram_receiver.get_message_text(message=message)

    assert message_text == {"text": message["text"], "entities": message["entities"]}


def test_process_text(telegram_receiver, telegram_message_with_entities):
    live_post_block = construct_live_post_block(
        message_id="1234", created=datetime.now()
    )
    text = telegram_receiver.get_message_text(
        message=telegram_message_with_entities["message"]
    )
    telegram_receiver.process_text(live_post=live_post_block, message_text=text)

    content = live_post_block["content"]
    assert content[0].value.source == "This post contains different type of entities."
    assert (
        content[1].value.source
        == 'This is a regular link <a href="https://github.com/">https://github.com/</a>.'
    )
    assert content[2].value.source == "This is a hashtag entity #WagtailLiveBot"
    assert (
        content[3].value.source
        == 'This is a link_text <a href="https://github.com/wagtail">wagtail</a>.'
    )


@override_settings(TELEGRAM_BOT_TOKEN="telegram-token")
def test_get_file_path(telegram_receiver, mocker):
    file_infos = {
        "ok": True,
        "result": {
            "file_id": "some-id",
            "file_unique_id": "some-id",
            "file_size": 31254,
            "file_path": "photos/file_1.jpg",
        },
    }
    mocker.patch.object(
        requests, "get", return_value=ResponseMock(ok=True, json_data=file_infos)
    )
    file_path = telegram_receiver.get_file_path(file_id="some_id")

    assert file_path == "photos/file_1.jpg"


def test_get_message_files_if_no_files(telegram_receiver, telegram_message):
    message = telegram_message["message"]
    message_files = telegram_receiver.get_message_files(message=message)

    assert message_files == []


def test_get_message_files_if_files(telegram_receiver, telegram_image_message, mocker):
    message = telegram_image_message["message"]
    photo = message["photo"][-1]
    photo["file_path"] = file_path = "photos/file_1.jpg"

    mocker.patch.object(
        TelegramWebhookReceiver, "get_file_path", return_value=file_path
    )
    message_files = telegram_receiver.get_message_files(message=message)

    assert message_files == [photo]


def test_get_image_title(telegram_receiver):
    image = {"file_path": "photos/file_1.jpg"}
    image_title = telegram_receiver.get_image_title(image=image)

    assert image_title == "file_1"


def test_get_image_name(telegram_receiver):
    image = {"file_path": "photos/file_1.jpg"}
    image_name = telegram_receiver.get_image_name(image=image)

    assert image_name == "file_1.jpg"


def test_get_image_mimetype_jpg(telegram_receiver):
    image = {"file_path": "photos/file_1.jpg"}
    image_mimetype = telegram_receiver.get_image_mimetype(image=image)

    assert image_mimetype == "jpeg"


def test_get_image_mimetype_other_mimetypes(telegram_receiver):
    image = {"file_path": "photos/file_1.other"}
    image_mimetype = telegram_receiver.get_image_mimetype(image=image)

    assert image_mimetype == "other"


def test_get_image_dimensions(telegram_receiver, telegram_image_message):
    message = telegram_image_message["message"]
    image = message["photo"][-1]
    image_dimensions = telegram_receiver.get_image_dimensions(image=image)

    assert image_dimensions == (image["width"], image["height"])


@override_settings(TELEGRAM_BOT_TOKEN="telegram-token")
def test_get_image_content(telegram_receiver, mocker):
    class ResponseMock:
        content = b""

    mocker.patch.object(requests, "get", return_value=ResponseMock())
    image_content = telegram_receiver.get_image_content(
        image={"file_path": "photos/file_1.jpg"}
    )

    assert isinstance(image_content, ContentFile)
    assert image_content.read() == b""


def test_get_message_id_from_edited_message(telegram_receiver, telegram_edited_message):
    message = telegram_edited_message["edited_message"]
    message_id = telegram_receiver.get_message_id_from_edited_message(message=message)

    assert message_id == telegram_receiver.get_message_id_from_message(message=message)


def test_get_message_text_from_edited_message(
    telegram_receiver, telegram_edited_message
):
    message = telegram_edited_message["edited_message"]
    message_text = telegram_receiver.get_message_text_from_edited_message(
        message=message
    )

    assert message_text == telegram_receiver.get_message_text(message=message)


def test_get_message_files_from_edited_message(
    telegram_receiver, telegram_edited_message
):
    message = telegram_edited_message["edited_message"]
    message_files = telegram_receiver.get_message_files_from_edited_message(
        message=message
    )

    assert message_files == telegram_receiver.get_message_files(message=message)


def test_embed_message(telegram_receiver, telegram_embed_message, blog_page_factory):
    live_post_block = construct_live_post_block(
        message_id="1234", created=datetime.now()
    )
    text = telegram_receiver.get_message_text(message=telegram_embed_message["message"])
    telegram_receiver.process_text(live_post=live_post_block, message_text=text)

    content = live_post_block["content"]
    assert content[0].value.source == "This is another test post."
    assert content[1].value.source == "This post contains an embed."
    assert content[2].block_type == EMBED
    assert content[2].value.url == "https://www.youtube.com/watch?v=Cq3LOsf2kSY"


def test_embed_message_2(
    telegram_receiver, telegram_embed_message_2, blog_page_factory
):
    live_post_block = construct_live_post_block(
        message_id="1234", created=datetime.now()
    )
    text = telegram_receiver.get_message_text(
        message=telegram_embed_message_2["message"]
    )
    telegram_receiver.process_text(live_post=live_post_block, message_text=text)

    content = live_post_block["content"]
    assert content[0].value.source == "This is another test post."
    assert content[1].value.source == (
        '<a href="https://www.youtube.com/watch?v=Cq3LOsf2kSY">'
        "https://www.youtube.com/watch?v=Cq3LOsf2kSY</a>. "
        "Some content here."
    )
    assert content[2].value.source == (
        "Some content here. "
        '<a href="https://www.youtube.com/watch?v=Cq3LOsf2kSY">'
        "https://www.youtube.com/watch?v=Cq3LOsf2kSY</a>"
    )


@pytest.mark.django_db
def test_add_media_message(
    telegram_receiver,
    telegram_media_message_1,
    telegram_media_message_2,
    blog_page_factory,
    mocker,
):
    page = blog_page_factory(channel_id="100")
    assert len(page.live_posts) == 0

    mocker.patch.object(
        TelegramWebhookReceiver, "get_file_path", return_value="photos/file_1.jpg"
    )
    mocker.patch.object(
        TelegramWebhookReceiver, "get_image_content", return_value=get_test_image_file()
    )

    telegram_receiver.dispatch_event(event=telegram_media_message_1)
    page.refresh_from_db()

    assert len(page.live_posts) == 1
    post_content = page.live_posts[0].value["content"]
    assert len(post_content) == 2
    assert post_content[1].block_type == IMAGE

    telegram_receiver.dispatch_event(event=telegram_media_message_2)
    page.refresh_from_db()

    assert len(page.live_posts) == 1
    post_content = page.live_posts[0].value["content"]
    assert len(post_content) == 3
    assert post_content[2].block_type == IMAGE


@pytest.mark.django_db
def test_add_media_message_wrong_channel(
    telegram_receiver,
    telegram_media_message_1,
    telegram_media_message_2,
    blog_page_factory,
    mocker,
):
    page = blog_page_factory(channel_id="100")
    assert len(page.live_posts) == 0

    mocker.patch.object(
        TelegramWebhookReceiver, "get_file_path", return_value="photos/file_1.jpg"
    )
    mocker.patch.object(
        TelegramWebhookReceiver, "get_image_content", return_value=get_test_image_file()
    )

    telegram_receiver.dispatch_event(event=telegram_media_message_1)
    page.refresh_from_db()

    assert len(page.live_posts) == 1
    post_content = page.live_posts[0].value["content"]
    assert len(post_content) == 2
    assert post_content[1].block_type == IMAGE

    telegram_media_message_2["message"]["chat"]["id"] = "99"
    telegram_receiver.dispatch_event(event=telegram_media_message_2)
    page.refresh_from_db()

    assert len(page.live_posts) == 1
    post_content = page.live_posts[0].value["content"]
    assert len(post_content) == 2
