import json

import pytest
from django.core.exceptions import ImproperlyConfigured
from wagtail.embeds.blocks import EmbedValue

from tests.testapp.models import BlogPage
from wagtail_live.receivers.base import EMBED, TEXT, BaseMessageReceiver


@pytest.fixture
def base_receiver():
    return BaseMessageReceiver()


def test_base_receiver_model(base_receiver):
    assert base_receiver.model == BlogPage


def test_receiver_model_live_app_setting_missing(base_receiver, settings):
    settings.WAGTAIL_LIVE_PAGE_MODEL = ""
    expected_err = "You haven't specified a live page model in your settings."
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        base_receiver.model


def test_receiver_model_bad_model(base_receiver, settings):
    settings.WAGTAIL_LIVE_PAGE_MODEL = "tests.testapp.models.RegularPage"
    expected_err = (
        "The live page model specified doesn't inherit from "
        "wagtail_live.models.LivePageMixin."
    )
    with pytest.raises(ImproperlyConfigured, match=expected_err):
        base_receiver.model


@pytest.mark.django_db
def test_get_live_page_from_channel_id(base_receiver, blog_page_factory):
    page = blog_page_factory(channel_id="some_id")
    got = base_receiver.get_live_page_from_channel_id(channel_id="some_id")
    assert got == page

    with pytest.raises(BlogPage.DoesNotExist):
        base_receiver.get_live_page_from_channel_id(channel_id="bad_id")


def test_get_embed(base_receiver):
    valid_embed = "https://www.youtube.com/watch?v=Wrc_gofwDR8"
    assert base_receiver.get_embed(valid_embed) == valid_embed

    invalid_embed = "some-text"
    assert base_receiver.get_embed(invalid_embed) == ""


@pytest.mark.django_db
def test_process_text(base_receiver, blog_page_factory):
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
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    live_post = page.get_live_post_by_index(live_post_index=0)

    valid_embed = "https://www.youtube.com/watch?v=Wrc_gofwDR8"
    msg = (
        "Live Post Title"
        + "\n"
        + "Check out Wagtail"
        + "\n"
        + valid_embed
        + "\n"
        + "Have fun!"
    )
    base_receiver.process_text(live_post, msg)

    post_content = live_post.value["content"]

    assert post_content[0].block_type == TEXT
    assert post_content[0].value == "Live Post Title"

    assert post_content[1].block_type == TEXT
    assert post_content[1].value == "Check out Wagtail"

    assert post_content[2].block_type == EMBED
    assert isinstance(post_content[2].value, EmbedValue)
    assert post_content[2].value.url == valid_embed

    assert post_content[-1].block_type == TEXT
    assert post_content[-1].value == "Have fun!"


@pytest.mark.django_db
def test_process_text_with_empty_content(base_receiver, blog_page_factory):
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
    page = blog_page_factory(channel_id="some-id", live_posts=live_posts)
    live_post = page.get_live_post_by_index(live_post_index=0)

    msg = "   "
    base_receiver.process_text(live_post, msg)

    # No block has been added
    assert len(live_post.value["content"]) == 0


# Abstract methods tests


def test_dispatch_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.dispatch_event(event={})


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


def test_get_image_title_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_image_title(image={})


def test_get_image_name_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_image_name(image={})


def test_get_image_mimetype_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_image_mimetype(image={})


def test_get_image_content_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_image_content(image={})


def test_get_image_dimensions_error_if_not_implemented(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_image_dimensions(image={})


def test_get_message_id_from_edited_message_error(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_id_from_edited_message(message={})


def test_get_message_text_from_edited_message_error(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_text_from_edited_message(message={})


def test_get_message_files_from_edited_message_error(base_receiver):
    with pytest.raises(NotImplementedError):
        base_receiver.get_message_files_from_edited_message(message={})
