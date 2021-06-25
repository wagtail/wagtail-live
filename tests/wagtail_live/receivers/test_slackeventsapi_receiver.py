import pytest

from tests.testapp.models import BlogPage
from wagtail_live import blocks
from wagtail_live.adapters.slack.receiver import SlackEventsAPIReceiver
from wagtail_live.receivers import TEXT


@pytest.fixture
def slack_receiver():
    return SlackEventsAPIReceiver()


def test_dispatch_new_message(slack_receiver, slack_message, mocker):
    mocker.patch.object(slack_receiver, "add_message")
    slack_receiver.dispatch(event=slack_message)

    message = slack_message["event"]
    slack_receiver.add_message.assert_called_once_with(message=message)


def test_dispatch_edited_message(slack_receiver, slack_edited_message, mocker):
    mocker.patch.object(slack_receiver, "change_message")
    slack_receiver.dispatch(event=slack_edited_message)

    message = slack_edited_message["event"]
    slack_receiver.change_message.assert_called_once_with(message=message)


def test_dispatch_deleted_message(slack_receiver, slack_deleted_message, mocker):
    mocker.patch.object(slack_receiver, "delete_message")
    slack_receiver.dispatch(event=slack_deleted_message)

    message = slack_deleted_message["event"]
    slack_receiver.delete_message.assert_called_once_with(message=message)


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


def test_get_message_id_from_edited_message(slack_receiver, slack_edited_message):
    message = slack_edited_message["event"]
    message_id = slack_receiver.get_message_id_from_edited_message(message=message)

    assert message_id == message["message"]["ts"]


def test_get_message_text_from_edited_message(slack_receiver, slack_edited_message):
    message = slack_edited_message["event"]
    message_text = slack_receiver.get_message_text_from_edited_message(message=message)

    assert message_text == message["message"]["text"]


def test_get__files_from_edited_message(slack_receiver, slack_edited_image_message):
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
    slack_embed_url = "<https://www.youtube.com/watch?v=Cq3LOsf2kSY>"
    got = slack_receiver.get_embed(text=slack_embed_url)

    assert got == slack_embed_url[1:-1]


def test_get_embed_if_not_embed(slack_receiver):
    assert slack_receiver.get_embed("Not embed") == ""


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
    assert content[0].value == message_parts[0]

    assert content[-1].block_type == TEXT
    assert content[-1].value == message_parts[-1]


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
    assert first_block.value == "This is another test post."

    # Edit the message
    edited_message = slack_edited_message["event"]
    slack_receiver.change_message(message=edited_message)

    message_added = BlogPage.objects.first().live_posts[-1]
    id_after_edit = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value == "This is another test post that has been edited."

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
    assert first_block.value == "This is another test post."

    edited_message = slack_edited_message["event"]
    edited_message["channel"] = "not_slack_channel"
    slack_receiver.change_message(message=edited_message)

    message_added = BlogPage.objects.first().live_posts[-1]
    id_after_edit = message_added.id
    first_block = message_added.value["content"][0]
    assert first_block.value == "This is another test post."

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
