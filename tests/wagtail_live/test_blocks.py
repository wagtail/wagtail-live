"""Wagtail Live blocks test suite."""

from datetime import datetime

import pytest
from wagtail.core.blocks import StreamValue, StructValue
from wagtail.embeds.blocks import EmbedValue
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image

from wagtail_live.blocks import (
    ContentBlock,
    LivePostBlock,
    add_block_to_live_post,
    clear_live_post_content,
    construct_embed_block,
    construct_image_block,
    construct_text_block,
)
from wagtail_live.receivers import TEXT


@pytest.fixture
def text_block():
    """Fixture representing a text block instance."""

    return construct_text_block(text="Some text")


def test_construct_text_block(text_block):
    """Text block is well constructed."""

    assert text_block == "Some text"


@pytest.fixture
def embed_block(valid_embed_url):
    """Fixture representing an embed block instance."""

    return construct_embed_block(valid_embed_url)


def test_construct_embed_block(valid_embed_url, embed_block):
    """Embed block is well constructed with url."""

    assert isinstance(embed_block, EmbedValue)
    assert embed_block.url == valid_embed_url


@pytest.fixture
def image_block(db):
    """Fixture representing an image block instance."""

    return construct_image_block(Image.objects.get(pk=1))


def test_construct_image_block(image_block):
    """Image block is well constructed with the id of the image provided."""

    assert image_block == ImageChooserBlock().to_python(1)


def test_construct_live_post_block(live_post_block):
    """LivePost block is well constructed with message id and creation date-time set."""

    assert live_post_block == StructValue(
        LivePostBlock(),
        {
            "message_id": "1234",
            "created": datetime(1970, 1, 1, 12, 00),
            "modified": None,
            "show": None,
            "content": StreamValue(ContentBlock(), []),
        },
    )


@pytest.fixture
def live_post_block_with_content(text_block, live_post_block):
    """Fixture representing a live post block instance filled with some content."""

    add_block_to_live_post(TEXT, text_block, live_post_block)
    return live_post_block


def test_add_block_to_live_post(text_block, live_post_block_with_content):
    """Live post block content contains text_block."""

    assert live_post_block_with_content["content"] == StreamValue(
        ContentBlock(), [("message", "Some text")]
    )


@pytest.fixture
def live_post_block_with_content_cleared(live_post_block_with_content):
    """Fixture representing a live post block which content has been cleared."""

    clear_live_post_content(live_post_block_with_content)
    return live_post_block_with_content


def test_clear_live_block_content_struct_value(live_post_block_with_content_cleared):
    """Live post block content is empty."""

    assert isinstance(live_post_block_with_content_cleared, StructValue)
    assert live_post_block_with_content_cleared["content"] == StreamValue(
        ContentBlock(), []
    )


def test_clear_live_block_content_stream_child(simple_live_page):
    """Live post block content is cleared."""

    first_post = simple_live_page.get_live_post_by_index(live_post_index=0)
    assert isinstance(first_post, StreamValue.StreamChild)
    assert first_post.value["content"] != StreamValue(ContentBlock(), [])

    clear_live_post_content(first_post)
    assert first_post.value["content"] == StreamValue(ContentBlock(), [])
