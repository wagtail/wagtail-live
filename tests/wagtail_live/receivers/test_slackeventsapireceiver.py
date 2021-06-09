"""Wagtail Live SlackEventsAPIReceiver class test suite."""

import json
import os
from unittest.mock import patch

import pytest
from django.conf import settings

from wagtail_live import blocks
from wagtail_live.receivers import TEXT

from ...testapp.models import SimpleLivePage

base_folder = os.path.join(settings.BASE_DIR, settings.PROJECT_DIR)
data_folder = base_folder + "/tests/wagtail_live/receivers/fixtures/"


def load_message_fixture(fixture_name):
    """Helper to load a json fixture.

    Args:
        fixture_name (str): filename of the fixture to load.
    """

    with open(os.path.join(data_folder, fixture_name)) as json_file:
        return json.load(json_file)


@pytest.fixture
def new_message(slack_receiver):
    """A new message payload as sent by Slack."""

    return load_message_fixture("slack_text_message.json")["event"]


def test_get_message_body(slack_receiver, new_message):
    """Retrieves the body - i.e what receivers need to know about an event."""

    event = load_message_fixture("slack_text_message.json")
    assert new_message == slack_receiver.get_message_body(event)


@pytest.fixture
def edited_message(slack_receiver):
    """An edited message payload as sent by Slack."""

    return load_message_fixture("slack_message_edited.json")["event"]


@pytest.fixture
def deleted_message(slack_receiver):
    """A deleted message payload as sent by Slack."""

    return load_message_fixture("slack_message_deleted.json")["event"]


@pytest.fixture
def embed_message(slack_receiver):
    """An embed message payload as sent by Slack."""

    return load_message_fixture("slack_embed_message.json")["event"]


@pytest.fixture
def image_message(slack_receiver):
    """An image message payload as sent by Slack."""

    return load_message_fixture("slack_image_message.json")["event"]


@pytest.fixture
def image_message_edited(slack_receiver):
    """An edited image message payload as sent by Slack."""

    return load_message_fixture("slack_image_message_edited.json")["event"]


def test_dispatch_new_message(slack_receiver, new_message):
    """Dispatches an new message event to add_message handler."""

    with patch.object(
        slack_receiver, "add_message", return_value=None
    ) as add_message_mock:
        slack_receiver.dispatch(new_message)

    add_message_mock.assert_called_once()


def test_dispatch_edited_message(slack_receiver, edited_message):
    """Dispatches an edited message event to change_message handler."""

    with patch.object(
        slack_receiver, "change_message", return_value=None
    ) as change_message_mock:
        slack_receiver.dispatch(edited_message)

    change_message_mock.assert_called_once()


def test_dispatch_deleted_message(slack_receiver, deleted_message):
    """Dispatches a deleted message event to delete_message handler."""

    with patch.object(
        slack_receiver, "delete_message", return_value=None
    ) as delete_message_mock:
        slack_receiver.dispatch(deleted_message)

    delete_message_mock.assert_called_once()


def test_get_channel_id_from_message(slack_receiver, new_message):
    """Retrieves the channel ID from a message."""

    channel_id = slack_receiver.get_channel_id_from_message(new_message)
    assert channel_id == new_message["channel"]


def test_get_message_id_from_message(slack_receiver, new_message):
    """Retrieves the message ID of a message."""

    message_id = slack_receiver.get_message_id_from_message(new_message)
    assert message_id == new_message["ts"]


def test_get_message_text(slack_receiver, new_message):
    """Retrieves the text of a message."""

    message_text = slack_receiver.get_message_text(new_message)
    assert message_text == new_message["text"]


def test_get_message_files_if_no_files(slack_receiver, new_message):
    """Returns empty list if the message doesn't contain files."""

    message_files = slack_receiver.get_message_files(new_message)
    assert message_files == []


def test_get_message_files_if_files(slack_receiver, image_message):
    """Returns list of files if the message contains files."""

    message_files = slack_receiver.get_message_files(image_message)
    assert message_files == image_message["files"]


def test_get_message_id_from_edited_message(slack_receiver, edited_message):
    """Returns the ID of the original message from an edited message event."""

    message_id = slack_receiver.get_message_id_from_edited_message(edited_message)
    assert message_id == edited_message["message"]["ts"]


def test_get_message_text_from_edited_message(slack_receiver, edited_message):
    """Returns the text of an edited message.."""

    message_text = slack_receiver.get_message_text_from_edited_message(edited_message)
    assert message_text == edited_message["message"]["text"]


def test_get__files_from_edited_message(slack_receiver, image_message_edited):
    """Returns a list of files from an edited message."""

    message_files = slack_receiver.get_message_files_from_edited_message(
        image_message_edited
    )
    assert message_files == image_message_edited["message"]["files"]


def test_get_files_from_edited_message_if_no_files(slack_receiver, edited_message):
    """Returns empty list if the edited message doesn't contain files."""

    message_files = slack_receiver.get_message_files_from_edited_message(edited_message)
    assert message_files == []


@pytest.fixture
def slack_embed_url():
    """Returns a Slack-like url."""

    return "<https://www.youtube.com/watch?v=Cq3LOsf2kSY>"


def test_get_embed_if_embed(slack_receiver, slack_embed_url):
    """Returns the url if the text provided is an embed url."""

    got = slack_receiver.get_embed_url(text=slack_embed_url)
    assert got == slack_embed_url[1:-1]


def test_get_embed_if_not_embed(slack_receiver):
    """Returns an empty string if the text provided isn't an embed url."""

    assert slack_receiver.get_embed_url("Not embed") == ""


@pytest.mark.django_db
def test_add_message(slack_receiver, new_message):
    """Message is added to live page with correct data and block types."""

    assert len(SimpleLivePage.objects.first().live_posts) == 5
    slack_receiver.add_message(new_message)

    live_page = SimpleLivePage.objects.first()
    assert len(live_page.live_posts) == 6

    live_post_added = live_page.live_posts[-1].value
    assert live_post_added["message_id"] == new_message["ts"]

    message_parts = new_message["text"].split("\n")
    content = live_post_added["content"]
    assert len(content) == len(message_parts)

    assert content[0].block_type == TEXT
    assert content[0].value == message_parts[0]

    assert content[-1].block_type == TEXT
    assert content[-1].value == message_parts[-1]


@pytest.mark.django_db
def test_add_message_inexistent_channel(slack_receiver, new_message):
    """Doesn't add message if a no live page corresponding to exists."""

    # Set wrong channel
    new_message["channel"] = "wrong_channel"

    with patch.object(
        blocks, "construct_live_post_block", return_value=None
    ) as construct_mock:
        slack_receiver.add_message(new_message)

    construct_mock.assert_not_called()


@pytest.mark.django_db
def test_change_message(slack_receiver, embed_message, edited_message):
    """Message is changed and new data is properly set."""

    # Add the message to edit
    slack_receiver.add_message(embed_message)

    message_added = SimpleLivePage.objects.first().live_posts[-1]
    previous_id = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value == "This is another test post."

    # Edit the message
    slack_receiver.change_message(edited_message)

    message_added = SimpleLivePage.objects.first().live_posts[-1]
    id_after_edit = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value == "This is another test post that has been edited."

    # ID is preserved.
    assert previous_id == id_after_edit


@pytest.mark.django_db
def test_change_message_wrong_channel(slack_receiver, embed_message, edited_message):
    """Doesn't edit message if no live page corresponding exists."""

    slack_receiver.add_message(embed_message)

    message_added = SimpleLivePage.objects.first().live_posts[-1]
    previous_id = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value == "This is another test post."

    edited_message["channel"] = "wrong_channel_name"
    slack_receiver.change_message(edited_message)

    message_added = SimpleLivePage.objects.first().live_posts[-1]
    id_after_edit = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value == "This is another test post."

    assert previous_id == id_after_edit


@pytest.mark.django_db
def test_delete_message(slack_receiver, embed_message, deleted_message):
    """Deletes a message."""

    slack_receiver.add_message(embed_message)
    assert len(SimpleLivePage.objects.first().live_posts) == 6

    slack_receiver.delete_message(deleted_message)
    assert len(SimpleLivePage.objects.first().live_posts) == 5


@pytest.mark.django_db
def test_delete_message_wrong_channel(slack_receiver, embed_message, deleted_message):
    """Doesn't delete message if no live page corresponding exists."""

    slack_receiver.add_message(embed_message)
    assert len(SimpleLivePage.objects.first().live_posts) == 6

    deleted_message["channel"] = "wrong_channel"
    slack_receiver.delete_message(deleted_message)
    assert len(SimpleLivePage.objects.first().live_posts) == 6


"""@pytest.mark.django_db
def test_process_files(slack_receiver, image_message, simple_live_page):
    files = slack_receiver.get_message_files(image_message)
    post = simple_live_page.live_posts[0]

    slack_receiver.process_files(post, files)
    post_content = post.value["content"]

    assert post_content[1].block_type == IMAGE
    assert isinstance(post_content[1].value, Image)
    assert post_content[1].value.title == files[0]["title"]"""
