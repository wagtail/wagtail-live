import json
from datetime import datetime

import pytest
from django.utils.timezone import now
from wagtail.core.blocks import StreamValue, StructValue
from wagtail.embeds.blocks import EmbedValue

from wagtail_live.blocks import (
    ContentBlock,
    LivePostBlock,
    add_block_to_live_post,
    clear_live_post_content,
    construct_embed_block,
    construct_live_post_block,
    construct_text_block,
)
from wagtail_live.receivers.base import TEXT


def test_construct_text_block():
    text_block = construct_text_block(text="Some text")
    assert text_block == "Some text"


def test_construct_embed_block():
    valid_embed = "https://www.youtube.com/watch?v=Wrc_gofwDR8"
    embed_block = construct_embed_block(url=valid_embed)

    assert isinstance(embed_block, EmbedValue)
    assert embed_block.url == valid_embed


def test_construct_live_post_block():
    live_post_block = construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    assert live_post_block == StructValue(
        LivePostBlock(),
        {
            "message_id": "1234",
            "created": datetime(1970, 1, 1, 12, 00),
            "modified": None,
            "show": True,
            "content": StreamValue(ContentBlock(), []),
        },
    )


def test_update_modified_field():
    live_post_block = construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )
    assert live_post_block["modified"] is None

    live_post_block["content"] = StreamValue(ContentBlock(), [("text", "Some text")])
    live_post_block.block.clean(live_post_block)

    last_modified = live_post_block["modified"]
    diff = now() - last_modified
    assert diff.total_seconds() == pytest.approx(0.0, abs=1)

    live_post_block["content"] = StreamValue(
        ContentBlock(), [("text", "Some text modified")]
    )
    live_post_block.block.clean(live_post_block)
    assert live_post_block["modified"] > last_modified


def test_add_block_to_live_post_structvalue():
    text_block = construct_text_block(text="Some text")
    live_post = construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )

    add_block_to_live_post(TEXT, text_block, live_post)

    assert isinstance(live_post, StructValue)
    assert live_post["content"] == StreamValue(ContentBlock(), [("text", "Some text")])


@pytest.mark.django_db
def test_add_block_to_live_post_streamchild(blog_page_factory):
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
    text_block = construct_text_block(text="Some text")

    add_block_to_live_post(TEXT, text_block, live_post)

    assert isinstance(live_post, StreamValue.StreamChild)
    assert live_post.value["content"] == StreamValue(
        ContentBlock(), [("text", "Some text")]
    )


def test_clear_live_post_content_structvalue():
    text_block = construct_text_block(text="Some text")
    live_post = construct_live_post_block(
        message_id="1234",
        created=datetime(1970, 1, 1, 12, 00),
    )

    add_block_to_live_post(TEXT, text_block, live_post)
    clear_live_post_content(live_post)

    assert isinstance(live_post, StructValue)
    assert live_post["content"] == StreamValue(ContentBlock(), [])


@pytest.mark.django_db
def test_clear_live_post_content_streamchild(blog_page_factory):
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
    text_block = construct_text_block(text="Some text")

    add_block_to_live_post(TEXT, text_block, live_post)
    clear_live_post_content(live_post)

    assert isinstance(live_post, StreamValue.StreamChild)
    assert live_post.value["content"] == StreamValue(ContentBlock(), [])
