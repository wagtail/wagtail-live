"""Wagtail Live BaseMessageReceiver class test suite."""

import pytest
from wagtail.embeds.blocks import EmbedValue

from wagtail_live.receivers import EMBED, TEXT, BaseMessageReceiver

from ...testapp.models import SimpleLivePage


@pytest.fixture
def base_receiver():
    """Fixture representing a base message receiver instance."""

    return BaseMessageReceiver("testapp", "SimpleLivePage")


def test_base_receiver_initialization(base_receiver):
    """Receiver model is properly set."""

    assert base_receiver.model == SimpleLivePage


@pytest.mark.django_db
def test_get_live_page_from_channel_id(base_receiver):
    """Retrieves the live page corresponding to the channel_id given."""

    expected = SimpleLivePage.objects.get(channel_id="12345")
    got = base_receiver.get_live_page_from_channel_id(channel_id="12345")
    assert expected == got


@pytest.mark.django_db
def test_get_live_page_from_channel_id_wrong_channel(base_receiver):
    """Raises DoesNotExist if a corresponding live page isn't found."""

    with pytest.raises(SimpleLivePage.DoesNotExist):
        SimpleLivePage.objects.get(channel_id="123456")


def test_get_embed_if_embed(base_receiver, valid_embed_url):
    """Returns the url if the text provided is an embed url."""

    assert base_receiver.get_embed_url(valid_embed_url) == valid_embed_url


def test_get_embed_if_not_embed(base_receiver):
    """Returns an empty string if the text provided isn't an embed url."""

    assert base_receiver.get_embed_url("Not embed") == ""


@pytest.mark.django_db
def test_process_text(base_receiver, simple_live_page, valid_embed_url):
    """Parses the text given and adds corresponding block types in live post."""

    msg = (
        "Live Post Title"
        + "\n"
        + "Check out Wagtail"
        + "\n"
        + valid_embed_url
        + "\n"
        + "Have fun!"
    )
    post = simple_live_page.live_posts[0]
    base_receiver.process_text(post, msg)

    post_content = post.value["content"]

    # Post already contains a message --> check from index 1
    assert post_content[1].block_type == TEXT
    assert post_content[1].value == "Live Post Title"

    assert post_content[2].block_type == TEXT
    assert post_content[2].value == "Check out Wagtail"

    assert post_content[3].block_type == EMBED
    assert isinstance(post_content[3].value, EmbedValue)
    assert post_content[3].value.url == valid_embed_url

    assert post_content[-1].block_type == TEXT
    assert post_content[-1].value == "Have fun!"


# Abstract methods tests


def test_dispatch_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.dispatch(message={})


def test_get_channel_id_from_message_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_channel_id_from_message(message={})


def test_get_message_id_from_message_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_id_from_message(message={})


def test_get_message_text_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_text(message={})


def test_get_message_files_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_files(message={})


def test_get_message_id_from_edited_message_error(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_id_from_edited_message(message={})


def test_get_message_text_from_edited_message_error(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_text_from_edited_message(message={})


def test_get_message_files_from_edited_message_error(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_files_from_edited_message(message={})
