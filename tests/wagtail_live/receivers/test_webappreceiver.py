import json

import pytest

from tests.testapp.models import BlogPage
from tests.utils import get_test_image_file
from wagtail_live import blocks
from wagtail_live.receivers import TEXT, BaseMessageReceiver
from wagtail_live.webapp.models import Channel, Image, Message
from wagtail_live.webapp.receiver import (
    MESSAGE_CREATED,
    MESSAGE_DELETED,
    MESSAGE_EDITED,
    WebAppReceiver,
)


@pytest.fixture
def webapp_receiver():
    return WebAppReceiver()


def test_webapp_receiver_instance(webapp_receiver):
    assert isinstance(webapp_receiver, BaseMessageReceiver)


@pytest.fixture
def message():
    return {
        "id": 1,
        "channel": "test_channel",
        "created": "2022-01-01T12:00:00",
        "modified": None,
        "show": True,
        "content": "Some content. \n More content here.",
        "images": [],
    }


def test_webapp_receiver_dispatch_new_msg(mocker, message, webapp_receiver):
    mocker.patch.object(WebAppReceiver, "add_message")
    message["update_type"] = MESSAGE_CREATED
    webapp_receiver.dispatch_event(event=message)

    WebAppReceiver.add_message.assert_called_once_with(message=message)


def test_webapp_receiver_dispatch_edit_msg(mocker, message, webapp_receiver):
    mocker.patch.object(WebAppReceiver, "change_message")
    message["update_type"] = MESSAGE_EDITED
    webapp_receiver.dispatch_event(event=message)

    WebAppReceiver.change_message.assert_called_once_with(message=message)


def test_webapp_receiver_dispatch_delete_msg(mocker, webapp_receiver):
    mocker.patch.object(WebAppReceiver, "delete_message")
    message = {
        "id": 1,
        "channel": "test_channel",
        "update_type": MESSAGE_DELETED,
    }
    webapp_receiver.dispatch_event(event=message)

    WebAppReceiver.delete_message.assert_called_once_with(message=message)


def test_get_channel_id_from_message(webapp_receiver, message):
    got = webapp_receiver.get_channel_id_from_message(message)
    assert got == message["channel"]


def test_get_message_id_from_message(webapp_receiver, message):
    got = webapp_receiver.get_message_id_from_message(message)
    assert got == message["id"]


def test_get_message_text(webapp_receiver, message):
    got = webapp_receiver.get_message_text(message)
    assert got == message["content"]


def test_get_message_files_if_no_files(webapp_receiver, message):
    got = webapp_receiver.get_message_files(message)
    assert got == []


@pytest.fixture
def edited_message(message):
    message["content"] = "Edited content"
    return message


@pytest.fixture
def image():
    return {
        "id": 1,
        "image": {
            "name": "test.jpg",
            "url": "/media/test.jpg",
            "width": 100,
            "height": 100,
        },
    }


def test_get_message_files_if_files(webapp_receiver, image, message):
    message["images"] = [image]
    got = webapp_receiver.get_message_files(message)
    assert got == [image]


def test_get_message_id_from_edited_message(webapp_receiver, edited_message):
    got = webapp_receiver.get_message_id_from_edited_message(edited_message)
    assert got == edited_message["id"]


def test_get_message_text_from_edited_message(webapp_receiver, edited_message):
    got = webapp_receiver.get_message_text_from_edited_message(edited_message)
    assert got == "Edited content"


def test_get_files_from_edited_message_no_files(webapp_receiver, edited_message):
    got = webapp_receiver.get_message_files_from_edited_message(edited_message)
    assert got == []


def test_get_files_from_edited_message_if_files(webapp_receiver, edited_message, image):
    edited_message["images"] = [image]
    got = webapp_receiver.get_message_files_from_edited_message(edited_message)
    assert got == [image]


def test_get_image_title(webapp_receiver, image):
    got = webapp_receiver.get_image_title(image)
    assert got == "test.jpg"


def test_get_image_name(webapp_receiver, image):
    got = webapp_receiver.get_image_name(image)
    assert got == "test.jpg"


def test_get_image_mimetype_jpg(webapp_receiver, image):
    got = webapp_receiver.get_image_mimetype(image)
    assert got == "jpeg"


def test_get_image_mimetype_other_formats(webapp_receiver, image):
    image["image"]["name"] = "test.other"
    got = webapp_receiver.get_image_mimetype(image)
    assert got == "other"


def test_get_image_dimensions(webapp_receiver, image):
    got = webapp_receiver.get_image_dimensions(image)
    assert got == (100, 100)


@pytest.mark.django_db
def test_get_image_content(webapp_receiver, image):
    channel = Channel.objects.create(channel_name="test_channel")
    message = Message.objects.create(channel=channel, content="Some content")

    image_content = get_test_image_file(filename="test.png", size=(100, 100))
    image_model = Image.objects.create(message=message, image=image_content)

    got = webapp_receiver.get_image_content(image=image)
    assert got == image_model.image


@pytest.mark.django_db
def test_add_message(blog_page_factory, webapp_receiver, message):
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

    webapp_receiver.add_message(message)

    page = BlogPage.objects.get(channel_id=message["channel"])
    assert len(page.live_posts) == 2

    post_added = page.live_posts[0].value
    assert post_added["message_id"] == message["id"]

    message_parts = message["content"].split("\n")
    content = post_added["content"]
    assert len(content) == len(message_parts)

    assert content[0].block_type == TEXT
    assert content[0].value == message_parts[0].strip()

    assert content[-1].block_type == TEXT
    assert content[-1].value == message_parts[-1].strip()


@pytest.mark.django_db
def test_add_message_inexistent_channel(mocker, webapp_receiver, message):
    message["channel"] = "wrong_channel"

    # construct_live_post_block is the first function called if a receiver finds a
    # page corresponding to the channel where the message was posted.
    mocker.patch.object(blocks, "construct_live_post_block")
    webapp_receiver.add_message(message)
    blocks.construct_live_post_block.assert_not_called()


@pytest.mark.django_db
def test_change_message(blog_page_factory, webapp_receiver, message):
    blog_page_factory(channel_id="test_channel")
    webapp_receiver.add_message(message)

    # Edit the message
    message["content"] = "Edited"
    webapp_receiver.change_message(message)

    message_edited = BlogPage.objects.first().live_posts[-1]
    content = message_edited.value["content"]

    # live post content should contain 1 block
    assert len(content) == 1

    first_block = content[0]
    assert first_block.value == "Edited"


@pytest.mark.django_db
def test_change_message_wrong_channel(blog_page_factory, webapp_receiver, message):
    blog_page_factory(channel_id="test_channel")
    webapp_receiver.add_message(message)

    # Edit the message and set wrong channel id
    message["content"] = "Edited"
    message["channel"] = "wrong_channel"
    webapp_receiver.change_message(message)

    message_edited = BlogPage.objects.first().live_posts[-1]
    content = message_edited.value["content"]

    # live post content shouldn't change
    assert len(content) == 2
    assert content[0].value == "Some content."
    assert content[-1].value == "More content here."


@pytest.mark.django_db
def test_delete_message(blog_page_factory, webapp_receiver, message):
    blog_page_factory(channel_id=message["channel"])
    webapp_receiver.add_message(message)
    assert len(BlogPage.objects.first().live_posts) == 1

    deleted_message = {
        "channel": message["channel"],
        "id": 1,
    }
    webapp_receiver.delete_message(deleted_message)
    assert len(BlogPage.objects.first().live_posts) == 0


@pytest.mark.django_db
def test_delete_message_wrong_channel(blog_page_factory, webapp_receiver, message):
    blog_page_factory(channel_id=message["channel"])
    webapp_receiver.add_message(message)
    assert len(BlogPage.objects.first().live_posts) == 1

    deleted_message = {
        "channel": "wrong_channel",
        "id": 1,
    }
    webapp_receiver.delete_message(deleted_message)
    assert len(BlogPage.objects.first().live_posts) == 1
