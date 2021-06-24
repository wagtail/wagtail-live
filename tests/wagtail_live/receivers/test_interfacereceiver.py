import json

import pytest

from tests.testapp.models import BlogPage
from wagtail_live import blocks
from wagtail_live.receivers import TEXT, BaseMessageReceiver
from wagtail_live_interface.receiver import (
    MESSAGE_CREATED,
    MESSAGE_DELETED,
    MESSAGE_EDITED,
    WagtailLiveInterfaceReceiver,
)


@pytest.fixture
def interface_receiver():
    return WagtailLiveInterfaceReceiver()


def test_interface_receiver_instance(interface_receiver):
    assert isinstance(interface_receiver, BaseMessageReceiver)


@pytest.fixture
def message():
    return {
        "id": 1,
        "channel": "test_channel",
        "created": "2022-01-01T12:00:00",
        "modified": None,
        "show": True,
        "content": "Some content. \n More content here.",
    }


def test_interface_receiver_dispatch_new_msg(mocker, message, interface_receiver):
    mocker.patch.object(WagtailLiveInterfaceReceiver, "add_message")
    message["update_type"] = MESSAGE_CREATED
    interface_receiver.dispatch_event(event=message)
    WagtailLiveInterfaceReceiver.add_message.assert_called_once_with(message=message)


def test_interface_receiver_dispatch_edit_msg(mocker, message, interface_receiver):
    mocker.patch.object(WagtailLiveInterfaceReceiver, "change_message")
    message["update_type"] = MESSAGE_EDITED
    interface_receiver.dispatch_event(event=message)
    WagtailLiveInterfaceReceiver.change_message.assert_called_once_with(message=message)


def test_interface_receiver_dispatch_delete_msg(mocker, interface_receiver):
    mocker.patch.object(WagtailLiveInterfaceReceiver, "delete_message")
    message = {
        "id": 1,
        "channel": "test_channel",
        "update_type": MESSAGE_DELETED,
    }
    interface_receiver.dispatch_event(event=message)
    WagtailLiveInterfaceReceiver.delete_message.assert_called_once_with(message=message)


def test_get_channel_id_from_message(interface_receiver, message):
    got = interface_receiver.get_channel_id_from_message(message)
    assert got == message["channel"]


def test_get_message_id_from_message(interface_receiver, message):
    got = interface_receiver.get_message_id_from_message(message)
    assert got == message["id"]


def test_get_message_text(interface_receiver, message):
    got = interface_receiver.get_message_text(message)
    assert got == message["content"]


def test_get_message_files_if_no_files(interface_receiver, message):
    got = interface_receiver.get_message_files(message)
    assert got == []


@pytest.mark.skip(reason="Unrealistic")
def test_get_message_files_if_files(interface_receiver, message):
    message["files"] = ["unrealistic-file"]
    got = interface_receiver.get_message_files(message)
    assert got == ["unrealistic-file"]


@pytest.fixture
def edited_message(message):
    message["content"] = "Edited content"
    return message


def test_get_message_id_from_edited_message(interface_receiver, edited_message):
    got = interface_receiver.get_message_id_from_edited_message(edited_message)
    assert got == edited_message["id"]


def test_get_message_text_from_edited_message(interface_receiver, edited_message):
    got = interface_receiver.get_message_text_from_edited_message(edited_message)
    assert got == "Edited content"


def test_get_files_from_edited_message_no_files(interface_receiver, edited_message):
    got = interface_receiver.get_message_files_from_edited_message(edited_message)
    assert got == []


@pytest.mark.skip(reason="Unrealistic")
def test_get_files_from_edited_message_if_files(interface_receiver, edited_message):
    edited_message["files"] = ["unrealistic-file"]
    got = interface_receiver.get_message_files_from_edited_message(edited_message)
    assert got == ["unrealistic-file"]


@pytest.mark.django_db
def test_add_message(blog_page_factory, interface_receiver, message):
    live_posts = json.dumps(
        [
            {
                "type": "live_post",
                "id": "some-id",
                "value": {
                    "message_id": "some-id",
                    "created": "2021-01-01T12:00:00",
                    "modified": "2021-01-01T12:00:00",
                    "show": True,
                    "content": [],
                },
            },
        ]
    )

    # Create a page with channel id of message
    page = blog_page_factory(channel_id=message["channel"], live_posts=live_posts)
    assert len(page.live_posts) == 1

    interface_receiver.add_message(message)

    page = BlogPage.objects.get(channel_id=message["channel"])
    assert len(page.live_posts) == 2

    post_added = page.live_posts[-1].value
    assert post_added["message_id"] == message["id"]

    message_parts = message["content"].split("\n")
    content = post_added["content"]
    assert len(content) == len(message_parts)

    assert content[0].block_type == TEXT
    assert content[0].value == message_parts[0]

    assert content[-1].block_type == TEXT
    assert content[-1].value == message_parts[-1]


@pytest.mark.django_db
def test_add_message_inexistent_channel(mocker, interface_receiver, message):
    message["channel"] = "wrong_channel"

    # construct_live_post_block is the first function called if a receiver finds a
    # page corresponding to the channel where the message was posted.
    mocker.patch.object(blocks, "construct_live_post_block")
    interface_receiver.add_message(message)
    blocks.construct_live_post_block.assert_not_called()


@pytest.mark.django_db
def test_change_message(blog_page_factory, interface_receiver, message):
    blog_page_factory(channel_id="test_channel")
    interface_receiver.add_message(message)

    # Edit the message
    message["content"] = "Edited"
    interface_receiver.change_message(message)

    message_edited = BlogPage.objects.first().live_posts[-1]
    content = message_edited.value["content"]

    # live post content should contain 1 block
    assert len(content) == 1

    first_block = content[0]
    assert first_block.value == "Edited"


@pytest.mark.django_db
def test_change_message_wrong_channel(blog_page_factory, interface_receiver, message):
    blog_page_factory(channel_id="test_channel")
    interface_receiver.add_message(message)

    # Edit the message and set wrong channel id
    message["content"] = "Edited"
    message["channel"] = "wrong_channel"
    interface_receiver.change_message(message)

    message_edited = BlogPage.objects.first().live_posts[-1]
    content = message_edited.value["content"]

    # live post content shouldn't change
    assert len(content) == 2
    assert content[0].value == "Some content. "
    assert content[-1].value == " More content here."


@pytest.mark.django_db
def test_delete_message(blog_page_factory, interface_receiver, message):
    blog_page_factory(channel_id=message["channel"])
    interface_receiver.add_message(message)
    assert len(BlogPage.objects.first().live_posts) == 1

    deleted_message = {
        "channel": message["channel"],
        "id": 1,
    }
    interface_receiver.delete_message(deleted_message)
    assert len(BlogPage.objects.first().live_posts) == 0


@pytest.mark.django_db
def test_delete_message_wrong_channel(blog_page_factory, interface_receiver, message):
    blog_page_factory(channel_id=message["channel"])
    interface_receiver.add_message(message)
    assert len(BlogPage.objects.first().live_posts) == 1

    deleted_message = {
        "channel": "wrong_channel",
        "id": 1,
    }
    interface_receiver.delete_message(deleted_message)
    assert len(BlogPage.objects.first().live_posts) == 1
